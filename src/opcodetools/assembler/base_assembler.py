import os

from opcodetools.assembler.exceptions import AssemblerException

class Assembler:

    def __init__(self,cpu):
        self.cpu = cpu
        self.make_frags()
        self.lines = None
        self.code = None
        self.defines = {}
        self.labels = {}
        
    def make_frags(self):
        '''Make opcode fragments for assembly

        The assembly processes needs the mnemonic broken up into fragments for matching.

        This method fills out the fragments for all opcodes. We assume that single lowercase
        letters represent things needing filled in.
        '''

        for op in self.cpu.opcodes:
            txt = op.mnemonic
            txt = self.remove_unneeded_whitespace(txt)            
            op.frags = ['']
            for i in range(len(txt)):
                c = txt[i]
                if c.islower():
                    op.frags.append(c)
                    if i < (len(txt) - 1):
                        # More to go -- start a new string for the more
                        op.frags.append('')
                else:
                    op.frags[-1] = op.frags[-1] + c
    
    def remove_unneeded_whitespace(self, text: str):
        '''Remove unneeded whitespace from a line of code
        
        ASSUMPTION: All opcodes are of the form
            LDA  (p,X)
        There are at most TWO terms separated by whitespace. All other whitespace
        can be removed.
        
        Args:
            text (str): the string

        Returns:
            str: the processed string
        '''
        
        i = text.find(' ')
        if i>=0:
            ret = text[0:i+1]+text[i+1:].replace(' ','')
        else:
            ret = text.replace(' ','')
            
        return ret.strip()
    
    def load_lines(self, filename: str):
        '''Load the lines from the given file

        This method also recurses into include files.

        The information about a line looks like is:
        {
            'file_name': 'test.asm',
            'line_number' : 4
            'text' : '   MOV A,#$50'
        }

        Args:
            filename (str): the name of the file

        Returns:
            list : list of line information from the file (and includes)        
        '''

        abst = os.path.abspath(filename)
        basep = os.path.dirname(abst)

        with open(filename, 'r') as f:
            raw_lines = f.readlines()

        ret = []
        pos = 0
        for line in raw_lines:
            pos += 1
            n = line.strip()
            if n.startswith('.include'):
                # TODO: error checking/reporting
                n = n[8:].strip()
                n = os.path.join(basep, n)
                ret = ret + self.load_lines(n)
                continue
            ret.append({
                'file_name': filename,
                'line_number': pos,
                'text': n
            })
        return ret

    def remove_comments_and_blanks(self, lines):
        '''Make a list of code lines (no blanks, no comments)

        For each line returned, the "original_text" has the unaltered

        Args:
            lines (list): complete list of lines from the files

        Returns:
            List : just the lines of code (and without comments)
        '''
        ret = []
        for line in lines:
            n = line['text']
            i = n.find(';')
            if i >= 0:
                n = n[0:i].strip()
            if n:
                line['original_text'] = line['text']
                line['text'] = n
                ret.append(line)
        return ret

    NON_SUB_CHARS = ',@#$~!?[]{}|' # Add as needed
    
    def find_opcode_for_text(self, text: str, assembler):
        '''Find the one opcode that best matches this line of text
        
        In finding the correct opcode, we parse out all the substitution
        pieces. That information is returned too.

        Args:
            text (str): the line of code
            assembler (Assembler): contains any defines

        Returns:
            Opcode: the requested (opcode,info) (or None)
        '''

        # Ignorable whitespace
        nmatch = self.remove_unneeded_whitespace(text)                
        
        possibles = []
        possibles_info = []
        shortest_frag = 10000 # Nice large number to start with
        for op in self.cpu.opcodes:
            remain = nmatch
            info = {}
            for fi in range(len(op.frags)):
                if not remain:
                    # We've reached the end of the test
                    # '' means match, None means no match
                    break
                # Next fragment of the opcode being tested
                frag = op.frags[fi]            
                if not frag[0].islower():
                    if remain.startswith(frag):
                        # This is a static fragment ... just peel it off
                        remain = remain[len(frag):]
                    else:
                        # This is a static fragment that doesn't match
                        remain = None # This opcode can't match
                else:
                    # This is a substitution                    
                    if fi==len(op.frags)-1:
                        # This is the last fragment ... match the rest of the line
                        i = len(remain)
                    else:                        
                        # Find the next fragment
                        i = remain.find(op.frags[fi+1])
                    if i>=0:
                        term = remain[:i]
                        info[frag[0]] = term                             
                        remain = remain[i:]
                        for c in self.NON_SUB_CHARS:
                            # These characters can't be in substitution parameters
                            # If we find any then this can't be a match
                            if c in term:
                                remain = None
                                break                                           
                    else:                
                        remain = None 
                            
            if remain != None:
                # This opcode is a potential ... add it to the list
                possibles.append(op)
                possibles_info.append(info)
                if len(op.frags)<shortest_frag:
                    shortest_frag = len(op.frags)
        
        # Rule out all but the most exact matches
        for i in range(len(possibles)-1,-1,-1):
            if len(possibles[i].frags)!=shortest_frag:
                del possibles[i]
                del possibles_info[i]
        
        n = len(possibles)
                        
        if n==0:
            # Not found
            return None
        
        if n==1:
            # Good! This is exactly the one we need.
            return (possibles[0],possibles_info[0])                
        
        # Multiple found. Try and pick one.
                
        if n==2 and possibles[0].frags[0]==possibles[1].frags[0]:
            # Special, common case where we can override the addressing mode
            # The mode might be forced with "<" or ">"
            # If not, we might have the address defined. If so, pick based on value.            
            if '>' in text:
                sz = 's2'
            elif '<' in text:
                sz = 's1'
            else:
                for k in possibles_info[0]:                
                    try:
                        v = self.parse_numeric(possibles_info[0][k])
                        if v<256:
                            sz = 's1'
                        else:
                            sz = 's2'
                    except:
                        # We don't know the size yet. Worst possible case.
                        sz = 's2'                
                    break
            # Find the opcode with the required size    
            for i in range(len(possibles)):
                op = possibles[i]
                for u in op.use:
                    if sz in op.use[u]:
                        return (op,possibles_info[i])
        
        raise AssemblerException('Multiple Matches')
    
    def fill_in_opcode(self, text, asm, address, op, pass_number):      
        opcode = op[0]
        info = op[1]  
        if pass_number == 0:            
            return [0] * len(opcode.code)
        else:            
            for key in info:                
                val = asm.parse_numeric(str(info[key]))
                if 'pcr' in opcode.use[key]:
                    val = val - (address+len(opcode.code))
                    if 's2' in opcode.use[key]:
                        if val<0:
                            val = val + 65536                        
                    else:
                        if val<0:
                            val = val + 256                                 
                info[key] = [info[key],val]                
            ret = []
            for c in opcode.code:
                if isinstance(c,str):
                    numval = info[c[0]][1]
                    # TODO: PCR
                    if c[1]=='1':
                        ret.append((numval>>8)&0xFF)
                    else:
                        ret.append((numval&0xFF))                    
                    #print('##',text,info,opcode.use)                    
                else:
                    ret.append(c)
            return ret    

    def process_data_term(self, line, pass_number: int, cur_term: str):
        '''Process a numerical value

        Args:
            line: the code line
            pass_number: 0 or 1
            cur_term: the term to parse
        Returns:
            List: a list of bytes (first-pass return all 0s)

        '''
        is_word = False
        if(cur_term.startswith('word ')):
            is_word = True
            cur_term = cur_term[5:].strip()
        elif(cur_term.startswith('byte ')):
            is_word = False
            cur_term = cur_term[5:].strip()

        if cur_term[0] >= '0' and cur_term[0] <= '9':
            cur_term = cur_term.replace('_', '')
            cur_term = cur_term.replace('.','0')

        if pass_number == 0:
            if is_word:
                return [0, 0]
            else:
                return [0]
        else:
            if is_word:
                return self.cpu.make_word(self.parse_numeric(cur_term))
            else:
                return [self.parse_numeric(cur_term)]

    def process_directive_data(self, line, pass_number: int):
        '''Process a data directive

        Creates the data list for a data-directive command

        Args:
            line : the code line
            pass_number : 0 or 1
        '''

        line['data'] = []

        cur_term = ''
        in_string = False

        for c in line['text'][1:]:
            if in_string:
                if c == '"':
                    in_string = False
                    for t in cur_term:
                        line['data'].append(ord(t))
                    cur_term = ''
                else:
                    cur_term = cur_term + c
            else:
                if c == '"':
                    in_string = True
                    cur_term = ''
                elif c == ',':
                    cur_term = cur_term.strip()
                    if cur_term:
                        dtt = self.process_data_term(line, pass_number, cur_term)
                        for d in dtt:
                            line['data'].append(d)
                    cur_term = ''
                else:
                    cur_term = cur_term + c

        if in_string:
            raise ASMException('Missing closing quotes', line)

        cur_term = cur_term.strip()
        if cur_term:
            dtt = self.process_data_term(line, pass_number, cur_term)
            for d in dtt:
                line['data'].append(d)

    def parse_numeric(self, s: str):
        '''Parse a numeric expression

        Uses the python eval to evalutate expressions,

        Args:
            s (str): the expression

        Returns:
            The evaluation value
        '''
        # TODO: I don't like this here. We need to parse these out while selecting opcodes.
        s = s.replace('>','')
        s = s.replace('<','')
        z = {**self.labels, **self.defines}
        v = eval(s, None, z)
        return v

    def process_define(self, line, pass_number: int):
        '''Process a define

        Defines are of the form .VAR = VALUE. This method adds to the
        growing list of defines.

        Args:
            line : the code line
            pass_number (int): 0 or 1

        '''

        n = line['text']
        #print('##',n)
        i = n.index('=')
        v = n[i + 1:].strip()
        n = n[1:i].strip()
        if pass_number == 2 and (n in self.labels or n in self.defines):
            # Second pass ... handle multiply-defined errors
            raise ASMException('Multiply defined: ' + n, line)
        if n.startswith('_'):
            # Handle configs
            self.process_config_define(n, v)
        else:
            # Must be a numeric expression
            v = self.parse_numeric(v)
            self.defines[n] = v

    def process_config_define(self, key: str, value: str):
        '''Process config defines

        Config defines are of the form ._VAR = VALUE.
        '''
        #if key == '_CPU':
        #    self.cpu = cpu.cpu_manager.get_cpu_by_name(value)
        #    self.cpu.init_assembly()
        #    if not self.cpu._opcodes[0].frags:
        #        self.cpu.make_frags()
        self.defines[key] = value

    def assemble(self):
        '''Two-pass assembly
        '''

        for pass_number in range(2):

            address = 0

            for line in self.code:

                n = line['text']

                if n.startswith('.'):
                    # Define (key = value)
                    i = n.find('"')  # In case the right side is a string, which might have '=' in it.
                    if i < 0:
                        i = len(n)
                    j = n.find('=')
                    if j < i and j>=0:
                        self.process_define(line, pass_number)

                    # Data (list of bytes/words)
                    elif n.startswith('. ') or n.startswith('.word ') or n.startswith('.byte '):
                        self.process_directive_data(line, pass_number)
                        line['address'] = address

                    else:
                        raise ASMException('Unknown directive: ' + n, line)

                elif n.endswith(':'):
                    # Label (or origin)
                    n = n[:-1].strip()
                    if pass_number == 0:
                        if n in self.labels or n in self.defines:
                            raise ASMException(
                                'Multiply defined: ' + n, line)

                    try:
                        # A number ... this is an origin
                        if n.upper().startswith('0X'):
                            address = int(n[2:], 16)
                        else:
                            address = int(n)
                    except:
                        # Not a number ... this is a label to remember
                        self.labels[n] = address
                else:
                    line['address'] = address
                    if not self.cpu:
                        raise ASMException('No CPU defined', line)
                    # Opcode
                    op = self.cpu.find_opcode_for_text(n, self)
                    if not op:
                        raise ASMException('Unknown opcode: ' + n, line)                    
                                        
                    # TODO: here
                    line['data'] = self.cpu.fill_in_opcode(n, self, address, op, pass_number)

                if 'data' in line:
                    address = address + len(line['data'])

    def write_listing(self, fname):
        with open(fname, 'w') as f:
            f.write('#### Labels\n')
            keys = self.labels.keys()
            keys = sorted(keys)
            for label in keys:
                f.write('{:16} = 0x{:04X}\n'.format(label, self.labels[label]))
            f.write('\n')
            f.write('#### Defines\n')
            keys = self.defines.keys()
            keys = sorted(keys)
            for define in keys:
                v = self.defines[define]
                if isinstance(v, str):
                    f.write('{:16} = {}\n'.format(define, v))
                else:
                    f.write('{:16} = 0x{:04X}\n'.format(define, v))
            f.write('\n')

            for line in self.lines:
                addr = ''
                if 'address' in line:
                    addr = '{:04X}:'.format(line['address'])
                data = ''
                if 'data' in line:
                    for d in line['data']:
                        data = data + '{:02X} '.format(d)
                data = data.strip()
                txt = line['text']
                if 'original_text' in line:
                    txt = line['original_text']
                f.write('{} {:16} {}\n'.format(addr, data, txt))

    def write_binary(self, name):        
        for line in self.lines:
            if 'address' in line:
                org = line['address']            
                break
                
        with open(name, 'wb') as f:
            for line in self.lines:
                if 'data' in line and line['data']:
                    new_org = line['address']
                    if new_org<org:
                        raise Exception('Origin problems')
                    while org<new_org:
                        f.write(bytearray([0xFF]))
                        org = org + 1
                    f.write(bytearray(line['data']))
                    org = org + len(bytearray(line['data']))
                    
    def assemble(self):
        '''Two-pass assembly
        '''

        for pass_number in range(2):

            address = 0

            for line in self.code:

                n = line['text']

                if n.startswith('.'):
                    # Define (key = value)
                    i = n.find('"')  # In case the right side is a string, which might have '=' in it.
                    if i < 0:
                        i = len(n)
                    j = n.find('=')
                    if j < i and j>=0:
                        self.process_define(line, pass_number)

                    # Data (list of bytes/words)
                    elif n.startswith('. ') or n.startswith('.word ') or n.startswith('.byte '):
                        self.process_directive_data(line, pass_number)
                        line['address'] = address

                    else:
                        raise AssemblerException('Unknown directive: ' + n, line)

                elif n.endswith(':'):
                    # Label (or origin)
                    n = n[:-1].strip()
                    if pass_number == 0:
                        if n in self.labels or n in self.defines:
                            raise AssemblerException(
                                'Multiply defined: ' + n, line)

                    try:
                        # A number ... this is an origin
                        if n.upper().startswith('0X'):
                            address = int(n[2:], 16)
                        else:
                            address = int(n)
                    except:
                        # Not a number ... this is a label to remember
                        self.labels[n] = address
                else:
                    line['address'] = address
                    if not self.cpu:
                        raise AssemblerException('No CPU defined', line)
                    # Opcode
                    op = self.find_opcode_for_text(n, self)
                    if not op:
                        raise AssemblerException('Unknown opcode: ' + n, line)                    
                                        
                    # TODO: here
                    line['data'] = self.fill_in_opcode(n, self, address, op, pass_number)

                if 'data' in line:
                    address = address + len(line['data'])