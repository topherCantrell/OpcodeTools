import unittest

import opcodetools.cpu.cpu_manager


class Test_CPUs(unittest.TestCase):

    def test_get_by_name(self):

        cp = opcodetools.cpu.cpu_manager.get_cpu_by_name('6502')
        self.assertTrue(cp != None)

        cp = opcodetools.cpu.cpu_manager.get_cpu_by_name('6803')
        self.assertTrue(cp != None)

        cp = opcodetools.cpu.cpu_manager.get_cpu_by_name('6809')
        self.assertTrue(cp != None)

        cp = opcodetools.cpu.cpu_manager.get_cpu_by_name('8052')
        self.assertTrue(cp != None)

        cp = opcodetools.cpu.cpu_manager.get_cpu_by_name('DVG')
        self.assertTrue(cp != None)

        cp = opcodetools.cpu.cpu_manager.get_cpu_by_name('Z80')
        self.assertTrue(cp != None)

        cp = opcodetools.cpu.cpu_manager.get_cpu_by_name('Z80GB')
        self.assertTrue(cp != None)
        
    def opcode_fillin_sanity(self,cp):        
        for op in cp.opcodes:
            lets = []
            for c in op.code:
                if isinstance(c,str):
                    if not c[0] in lets:
                        lets.append(c[0])
            bs = op.use                
            if not lets:
                #print("##",lets,'##',bs,'##',op.mnemonic)
                self.assertTrue(bs=={})
                continue                
            self.assertTrue(len(lets),len(bs))
            for let in lets:
                #print('##',let,'##',bs,'##',op.mnemonic)
                self.assertTrue(let in bs)
                
    def test_opcode_sanity(self):
        cp = opcodetools.cpu.cpu_manager.get_cpu_by_name('6502')
        self.opcode_fillin_sanity(cp)
        cp = opcodetools.cpu.cpu_manager.get_cpu_by_name('6803')
        self.opcode_fillin_sanity(cp)
        cp = opcodetools.cpu.cpu_manager.get_cpu_by_name('6809')
        self.opcode_fillin_sanity(cp)
        cp = opcodetools.cpu.cpu_manager.get_cpu_by_name('8052')
        self.opcode_fillin_sanity(cp)
        cp = opcodetools.cpu.cpu_manager.get_cpu_by_name('DVG')
        self.opcode_fillin_sanity(cp)
        cp = opcodetools.cpu.cpu_manager.get_cpu_by_name('Z80')
        self.opcode_fillin_sanity(cp)
        cp = opcodetools.cpu.cpu_manager.get_cpu_by_name('Z80GB')
        self.opcode_fillin_sanity(cp)

    
    
    

