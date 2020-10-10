import os
import unittest

import opcodetools.assembler.assembler


TEST_DIR = os.path.dirname(__file__)


class Test_Assembly(unittest.TestCase):

    def test_assemble(self):

        asm = opcodetools.assembler.assembler.Assembler(TEST_DIR + '/../doublegap/DoubleGap.asm')

        asm.assemble()

        asm.write_listing('test.lst')
        asm.write_binary('test.bin')

        with open(TEST_DIR + '/../doublegap/DoubleGap.bin', 'rb') as f:
            expected_dat = f.read()

        with open('test.bin', 'rb') as f:
            test_dat = f.read()

        for i in range(len(test_dat)):
            if test_dat[i] != expected_dat[i]:
                print('Different at ' + hex(i))

        self.assertEqual(test_dat, expected_dat)
