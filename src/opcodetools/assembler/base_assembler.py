import os

from opcodetools.assembler.exceptions import AssemblerException

class Assembler:

    def __init__(self,cpu):
        self.cpu = cpu
        self.make_frags()
        self.lines = None
        self.code = None
        
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
           
    NON_SUB_CHARS = ',@#$~!?[]{}|' # Add as needed
    
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
                # TODO error checking/reporting
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
        shortest_frag = 10000
        for op in self._opcodes:
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
            return (possibles[0],possibles_info[0])                
        
        # Multiple found. Try and pick one.
                
        if n==2 and possibles[0].frags[0]==possibles[1].frags[0]:
            # Special, common case where we can override the addressing mode
            # The mode might be forced with "<" or ">"
            # If not, we might have the address defined. If so, pick based on value.
            sz = 's2'            
            #if '_default_base_page' in assembler.defines and assembler.defines['_default_base_page']=='true':
            #    sz = 's1'
            if '>' in text:
                sz = 's2'
            elif '<' in text:
                sz = 's1'
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
                    op = self.cpu.find_opcode_for_text(n, self)
                    if not op:
                        raise AssemblerException('Unknown opcode: ' + n, line)                    
                                        
                    # TODO: here
                    line['data'] = self.cpu.fill_in_opcode(n, self, address, op, pass_number)

                if 'data' in line:
                    address = address + len(line['data'])
                