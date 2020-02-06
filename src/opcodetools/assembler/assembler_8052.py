import opcodetools.assembler.base_assembler

class Assembler8052(opcodetools.assembler.base_assembler.Assembler):
    
    def __init__(self,cpu):
        super().__init__(cpu)
    
        # TODO: the 8052_SFR.asm includes (allow user to override that file)