# TODO substitue "$" with "0x" in numerics
# TODO isbyte/isword flags for data persist between terms
# TODO better data dump for large datas (tools)

import os

import opcodetools.cpu.cpu_manager
from typing import List

import importlib


class ASMException(Exception):
    def __init__(self, message, line):
        super().__init__(message)
        self.line = line


class Assembler:

    '''Manages labels and controls the assembly process
    '''

    def __init__(self, filename: str):
        '''Create a new Assembler object

        Args:
            filename (string) name of file to assemble
        '''

        self.lines = self.load_lines(filename)
        self.code = self.remove_comments_and_blanks(self.lines)
        self.collect_labels(self.code)
        self.defines = {}
        self.labels = {}
        self.cpu = None        

    def load_lines(self, filename: str) -> List[dict]:
        '''Load the lines from the given file

        This method also recurses into included files.

        The information about a line looks like is:
        {
            'file_name'     : 'test.asm'
            'line_number'   : 4
            'text'          : 'MOV A,#$50'
            'original_text' : '  MOV    A, #$50'
            'address'       : 0x4000
            TODO 'label'         : 'main:'
            'data'          : [1,2,3,4]            
            'tool_line_no'       : ...
            'tool_end_of_block'  : ... Information for an external tool
            'tool_text_of_block' : ...
            'tool_module'        : ...
        }

        Args:
            filename (str): the name of the file

        Returns:
            list : list of line information from the file (and includes)
        '''

        absn = os.path.abspath(filename)
        basep = os.path.dirname(absn)

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
                try:
                    ret = ret + self.load_lines(n)
                except FileNotFoundError:
                    raise ASMException('Could not find file ' + n, {'file_name': n, 'line_number': pos, 'text': line})
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

    def collect_labels(self, lines):
        for line in lines:
            n = line['text']
            i = n.find(' ')
            if i<0:
                i = len(n)
            lab = n[0:i]
            if lab.endswith(':'):
                # This is a label
                line['label'] = lab
                line['text'] = n[i:].strip()                

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

        if pass_number == 0:
            if is_word:
                return [0, 0]
            else:
                return [0]
        else:
            try:
                ret = self.parse_numeric(cur_term)
                if is_word:                    
                    if ret > 65535:
                        raise ASMException('Value is larger than two bytes', line)
                    return self.cpu.make_word(ret)
                else:                    
                    if ret > 255:
                        raise ASMException('Value is larger than one byte', line)
                    return [ret]
            except ASMException:
                raise
            except Exception:
                raise ASMException('Invalid numeric value: ' + cur_term, line)

    def process_tool(self, line, line_no, pass_number):
        # Return the next line number (allows us to consume multiple lines)
        
        if pass_number==0:
            # Find the end of the block on the first pass
            # TODO ERROR IF WE DON'T FIND IT
            tool_info = line['text'].split()
            mod_name = tool_info[1]
            if len(tool_info)>3:
                mod_fun = tool_info[2]
            else:
                mod_fun = 'doAsmTool'       
            text_of_block = []
            end_of_block = line_no
            while self.code[end_of_block]['text'] != '}':
                text_of_block.append(self.code[end_of_block]['text'])
                end_of_block += 1
            line['tool_line_no'] = line_no
            line['tool_end_of_block'] = end_of_block
            line['tool_text_of_block'] = text_of_block
            line['tool_module'] = importlib.import_module(mod_name)   
            line['tool_function'] = mod_fun         
        else:
            end_of_block = line['tool_end_of_block']

        fn = getattr(line['tool_module'],line['tool_function'])
        
        fn(self,line,pass_number,line['tool_text_of_block'])

        return end_of_block + 1
        

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
        if s.startswith('_'):
            s = self.scope + s
        # Dollar for hex is very common in assembly
        s = s.replace('$','0x')
        if s[0] >= '0' and s[0] <= '9':            
            s = s.replace('.', '0') # For simple ascii art
        # TODO the addressing mode < and > should be handled elsewhere
        if s[0] == '<' or s[0] == '>':
            s = s[1:]
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
        i = n.index('=')
        v = n[i + 1:].strip()
        n = n[1:i].strip()
        if pass_number == 2 and (n in self.labels or n in self.defines):
            # Second pass ... handle multiply-defined errors
            raise ASMException('Multiply defined: ' + n, line)
        
        # Must be a numeric expression
        try:
            v = self.parse_numeric(v)
            self.defines[n] = v
        except Exception:
            raise ASMException('Invalid numeric constant: ' + v, line)    

    def assemble(self):
        '''Two-pass assembly
        '''

        for pass_number in range(2):

            self.scope = ''
            address = 0

            num_lines = len(self.code)
            line_no = 0
            while line_no < num_lines:            

                line = self.code[line_no]
                line_no += 1                

                if 'label' in line:
                    # Label (or origin)
                    n = line['label'][:-1]
                    if n.startswith('_'):
                        n = self.scope + n
                    else:                        
                        self.scope = n
                    
                    if pass_number == 0:
                        if n in self.labels or n in self.defines:
                            raise ASMException('Multiply defined: ' + n, line)

                    try:
                        # Purely numeric? This is an "origin"
                        a = self.parse_numeric(n)
                        address = a
                        self.scope = ''
                    except Exception:
                        # Not a number ... this is a label to remember
                        self.labels[n] = address

                n = line['text']

                if n.startswith('.'):
                    # These are directives to the assembler

                    if n.upper().startswith('.CPU '):
                        # Define the CPU
                        value = n[5:].strip()
                        self.cpu = opcodetools.cpu.cpu_manager.get_cpu_by_name(value)
                        if not self.cpu:
                            raise ASMException('Unknown CPU: ' + value, line)
                        self.cpu.init_assembly()
                        if not self.cpu._opcodes[0].frags:
                            # TODO revisit the assembly process ... might be easier than this
                            self.cpu.make_frags()
                    
                    elif n.startswith('.tool '):
                        # External data tools
                        line['address'] = address
                        line_no = self.process_tool(line,line_no, pass_number)                                            
                    
                    elif n.startswith('. ') or n.startswith('.word ') or n.startswith('.byte '):
                        # Data (list of bytes/words)
                        line['address'] = address
                        self.process_directive_data(line, pass_number)        

                    elif '=' in n:
                        # Define (key = value)
                        # The value is ALWAYS numeric                        
                        self.process_define(line,pass_number)                

                    else:
                        raise ASMException('Unknown directive: ' + n, line)                

                elif n:
                    # Must be a line of assembly
                    
                    line['address'] = address
                    if not self.cpu:
                        raise ASMException('No CPU defined', line)

                    # Opcode
                    op = self.cpu.find_opcode_for_text(n, self)
                    if not op:
                        raise ASMException('Unknown opcode: ' + n, line)

                    #try:
                    line['data'] = self.cpu.fill_in_opcode(n, self, address, op, pass_number)
                    # TODO we don't want to supress errors from the code
                    #except Exception as f:
                    #    raise ASMException(str(f), line)

                else:
                    # Lines with only a label get here
                    pass

                if 'data' in line:
                    address = address + len(line['data'])

    def write_labels(self, fname):
        """write the label definitions to an includable file
        Args:
            fname : the filename to create
        """
        with open(fname, 'w') as f:
            f.write("; DO NOT EDIT THIS FILE\n")
            f.write("; This file is generated by the assembler\n")
            f.write("")
            keys = self.labels.keys()
            keys = sorted(keys)
            for label in keys:
                if not label.startswith('_'):
                    f.write('.{:16} = 0x{:04X}\n'.format(label, self.labels[label]))
            f.write('\n')

    def write_listing(self, fname):
        '''Write the listing file

        Args:
            fname : the filename to create
        '''
        with open(fname, 'w') as f:
            f.write('#### Labels\n')
            keys = self.labels.keys()
            keys = sorted(keys)
            for label in keys:
                if not label.startswith('_'):
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
                if '.tool' in line['text']:
                    pos = 0
                    addr = line['address']
                    for d in line['data']:
                        if pos == 0:
                            f.write('{:04X}:'.format(addr))
                        f.write(' {:02X}'.format(d))
                        pos += 1
                        if pos==32:
                            f.write('\n')
                            pos = 0
                            addr+=32
                    if pos:
                        f.write('\n')
                else:
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
        '''Write the binary file

        Args:
            fname : the filename to create
        '''
        for line in self.lines:
            if 'address' in line:
                org = line['address']
                break
        with open(name, 'wb') as f:
            for line in self.lines:
                if 'data' in line and line['data']:
                    new_org = line['address']
                    if new_org < org:
                        raise Exception('Origin problems')
                    while org < new_org:
                        f.write(bytearray([0xFF]))
                        org = org + 1
                    f.write(bytearray(line['data']))
                    org = org + len(bytearray(line['data']))
