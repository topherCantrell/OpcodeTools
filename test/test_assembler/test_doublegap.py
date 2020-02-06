import unittest

import opcodetools.assembler.assembler_manager


class Test_DoubleGap(unittest.TestCase):

    def test_assemble(self):
        
        asm = opcodetools.assembler.assembler_manager.get_assembler_by_name('6502')
        
        lines = asm.load_lines('DoubleGap.asm')
        asm.lines = lines
        asm.code = asm.remove_comments_and_blanks(lines)
        
        asm.assemble()
        
        asm.write_listing('test.lst')
        
        asm.write_binary('test.bin')