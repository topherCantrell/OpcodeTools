import opcodetools.assembler.base_assembler

class Assembler8051(opcodetools.assembler.base_assembler.Assembler):
    
    def __init__(self,cpu):
        super().__init__(cpu)
        
    def resolve_multiple_opcodes(self, possibles, possibles_info,pass_number):        
        
        for cop in possibles:
            if cop.mnemonic != 'ACALL p' and cop.mnemonic != 'AJUMP p':
                return super().resolve_multiple_opcodes(possibles, possibles_info)
        if pass_number==0:
            return (possibles[0],possibles_info[0])
            
        bo = 0x01 # For AJMP
        if possibles[0].mnemonic == 'ACALL p':
            bo = 0x11 # For JCALL
                
        addr = self.parse_numeric(possibles_info[0]['p'])
        uaddr = addr>>8
        uaddr = (uaddr << 5) | bo
                
        for i in range(len(possibles)):        
            if possibles[i].code[0] == bo:
                return (possibles[i],possibles_info[i])
                        
        return super().resolve_multiple_opcodes(possibles, possibles_info,pass_number)
            
        # TODO: the 8052_SFR.asm includes (allow user to override that file)