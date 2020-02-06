'''
 
  Example opcodes:
  
    DATA       MMNEMONIC     CPU   USE
    10 a0 a1 : JSR a         6502  (a=code)
    90 aa    : BCC a         6502  (a=code_pcr)
    21 aa    : AND (a,X)     6502  (a=ram)
    69 aa    : ADC #a        6502  (a=const)
    D3 aa    : OUT (a),A     Z80   (a=port_w)
    6C a0 a1 : JMP (a)       6502  (a=code)
    10 aa bb : JBC a,b       6502  (a=ram_bit,b=code)  
    85 bb aa : MOV a,b       6502  (a=ram,b=ram)
    
  The actual substitution letters don't matter (as long as they are lower-case). The letters map to byte
  positions in the opcode data.
  
  Multibyte substitutions list the order of the bytes. 0 is the least significant, 1 is next, and so on.
  A little-endian address would be: a0a1
  
  TODO: this "use" about picking a set of labels to search for matches
  
  The "use" field describes how the substitutions are used:
    - const (an immediate constant)
    - data  (address is a regular read/write memory access)
    - code  (address is a code destination for jumps)
    - port  (address is a port read/write memory access)
    
  Direction qualifiers include (direction often matters for I/O addresses):
    - _r  The address is read from
    - _w  The address is written to
    - _rw The adress is read and written back to

  The _pcr qualifier indicates the actual address is relative to the program counter.
  
  Size (calculated):
    - _s1 The substitution is 1 byte (default if not given)
    - _s2 The substitution is 2 byte 
   
  Some processors have their own substitution qualifiers.
  
  Qualifiers - 6809 specific
    _pair  Pair of registers
    _pshs  Register list (push to S)
    _puls  Register list (pull from S)
    _pshu  Register list (push to U)
    _pulu  Register list (pull from U)
    _bp    BasePage *
    
    * The 6809 has a BP register (not always 00). Thus address 0010 and address >10 could be different.
    Other processors have shortcuts for 1 byte addresses, but the upper byte is always 00 such
    that 0010 and >10 are the same.
  
  Qualifiers - 8051 specific  
    _bit  Bit address
    _11   11_bit address (3 bits in opcode)
 

'''
from opcodetools.cpu.opcode import Opcode
from opcodetools.cpu.exceptions import CPUException

class CPU:

    cpu_singletons = {}

    def __init__(self, opcodes: list):
        self.opcodes = []
        self.opcodes_info = opcodes
        self.quick_codes = {}
        for op in opcodes:
            opc = self.make_opcode(op)
            opc.cpu = self
            self.opcodes.append(opc)
            key = opc.code[0]
            if not isinstance(key, int):
                raise CPUException('First code byte must be a number')
            if key in self.quick_codes:
                self.quick_codes[key].append(opc)
            else:
                self.quick_codes[key] = [opc]

        # Show opcodes with more than 1 fill-in
        #letters = []
        # for d in opc.code():
        #    if isinstance(d,str):
        #        if not d[0] in letters:
        #            letters.append(d[0])
        # if len(letters)>1:
        #    print(opc.get_mnemonic())

    def make_opcode(self, info: dict)->Opcode:
        '''Create an opcode from the given info.

        This is a factory method to allow for overrides

        Args:
            info (dict): the opcode information
        Returns:
            Opcode: factoried opcode
        '''
        return Opcode(info)
    
    def is_little_endian(self):
        '''Returns True if this CPU is little endian.'''
        return True
    
    def make_word(self,term:int):        
        '''Convert a number to a two-byte value
        
        Args:
            term (int): the number
        Returns:
            list of two bytes in endian-order
        '''        
        a = term & 0xFF
        b = (term >> 8)&0xFF
        if self.is_little_endian():
            return [a,b]
        else:
            return [b,a]