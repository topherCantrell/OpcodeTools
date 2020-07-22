import opcodetools.assembler.base_assembler
import opcodetools.cpu.cpu_manager

def get_assembler_by_name(name:str) -> opcodetools.assembler.base_assembler.Assembler:
    
    cp = opcodetools.cpu.cpu_manager.get_cpu_by_name(name)
    
    if name == '6502':
        return opcodetools.assembler.base_assembler.Assembler(cp)
    elif name == '6803':
        return None
    elif name == '6809':
        return None
    elif name == '8051':
        from opcodetools.assembler.assembler_8051 import Assembler8051
        return Assembler8051(cp)
    elif name == 'DVG':
        return None
    elif name == 'Z80':
        return None
    elif name == 'Z80GB':
        return None
    