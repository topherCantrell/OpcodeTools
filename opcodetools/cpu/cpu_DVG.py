import opcodetools.cpu.base_cpu

OPCODES = [
    {"mnemonic": "VEC SCALE=0, BRI=b, X=x, Y=y",   "code": "0000_0yyy_yyyy_yyyy bbbb_0xxx_xxxx_xxxx",   "use": ""},
    {"mnemonic": "VEC SCALE=1, BRI=b, X=x, Y=y",   "code": "0001_0yyy_yyyy_yyyy bbbb_0xxx_xxxx_xxxx",   "use": ""},
    {"mnemonic": "VEC SCALE=2, BRI=b, X=x, Y=y",   "code": "0010_0yyy_yyyy_yyyy bbbb_0xxx_xxxx_xxxx",   "use": ""},
    {"mnemonic": "VEC SCALE=3, BRI=b, X=x, Y=y",   "code": "0011_0yyy_yyyy_yyyy bbbb_0xxx_xxxx_xxxx",   "use": ""},
    {"mnemonic": "VEC SCALE=4, BRI=b, X=x, Y=y",   "code": "0100_0yyy_yyyy_yyyy bbbb_0xxx_xxxx_xxxx",   "use": ""},
    {"mnemonic": "VEC SCALE=5, BRI=b, X=x, Y=y",   "code": "0101_0yyy_yyyy_yyyy bbbb_0xxx_xxxx_xxxx",   "use": ""},
    {"mnemonic": "VEC SCALE=6, BRI=b, X=x, Y=y",   "code": "0110_0yyy_yyyy_yyyy bbbb_0xxx_xxxx_xxxx",   "use": ""},
    {"mnemonic": "VEC SCALE=7, BRI=b, X=x, Y=y",   "code": "0111_0yyy_yyyy_yyyy bbbb_0xxx_xxxx_xxxx",   "use": ""},
    {"mnemonic": "VEC SCALE=8, BRI=b, X=x, Y=y",   "code": "1000_0yyy_yyyy_yyyy bbbb_0xxx_xxxx_xxxx",   "use": ""},
    {"mnemonic": "VEC SCALE=9, BRI=b, X=x, Y=y",   "code": "1001_0yyy_yyyy_yyyy bbbb_0xxx_xxxx_xxxx",   "use": ""},
    {"mnemonic": "CUR SCALE=s, X=t, Y=u",          "code": "1010_00yy_yyyy_yyyy ssss_00xx_xxxx_xxxx",   "use": ""},
    {"mnemonic": "HALT",                           "code": "1011_0000_0000_0000",                       "use": ""},
    {"mnemonic": "JSR a",                          "code": "1100_aaaa_aaaa_aaaa",                       "use": "a=code"},
    {"mnemonic": "RTS",                            "code": "1101_0000_bbbb_bbbb",                       "use": ""},
    {"mnemonic": "JMP a",                          "code": "1110_aaaa_aaaa_aaaa",                       "use": "a=code"},
    {"mnemonic": "SVEC SCALE=c, BRI=b, X=d, Y=y",  "code": "1111_gyyy_bbbb_hxxx",                       "use": "", "notes": "h is upper bit of c, g is lower bit", }
]

'''
      aa bb
0858: DB F0

      Xxx       Yyy
1101_1011 1111_0000

y = 0 *256 = 0
x = 3 *256 = 768
'''


class CPU_DVG(opcodetools.cpu.base_cpu.CPU):

    def __init__(self):        
        self._dvg_copcodes = []

        for entry in OPCODES:
            entry['code'] = entry['code'].replace('_', '').replace(' ', '')
            # Note that these are BIT fields ... not BYTE fields like other
            # CPUs
            self._dvg_copcodes.append(entry)
            
        super().__init__(self._dvg_copcodes)
            
    def find_opcodes_for_binary(self, binary: list, exact: bool=False) -> list:
        
        if not exact:
            raise Exception('Still working on a generic DVG disassembler')
        
        leading = binary[1] >> 4
        return [ self._opcodes[leading] ]
    
