import unittest

import opcodetools.cpu.cpu_manager


class Test_CPUs(unittest.TestCase):        
       
    def test_disassembly(self):

        cp = opcodetools.cpu.cpu_manager.get_cpu_by_name('6809')
        opc = cp.find_opcodes_for_binary([0x10, 0xA3, 0x9D, 1, 2])
        self.assertTrue(len(opc) == 1)
        opc = opc[0]
        self.assertTrue(opc.mnemonic == 'CMPD [k,PC]')    

    def test_binary_to_string(self):

        cp = opcodetools.cpu.cpu_manager.get_cpu_by_name('6809')

        binary = [0x10, 0xA3, 0x9D, 1, 2]
        opc = cp.find_opcodes_for_binary(binary)[0]

        fills = cp.get_mnemonic_fills(opc, 0x1000, binary)
        out = cp.binary_to_string(opc, 0x1000, binary, fills)        
                
        print('##',out)
        self.assertTrue(out.strip()=='1000: 10 A3 9D 01 02  CMPD    [$1107,PC]')   

    def test_one_byte_relative(self):

        cp = opcodetools.cpu.cpu_manager.get_cpu_by_name('6809')
        binary = [0x26, 0xF9]
        opc = cp.find_opcodes_for_binary(binary)[0]
        fills = cp.get_mnemonic_fills(opc, 0xC050, binary)

        out = cp.binary_to_string(opc, 0xC050, binary, fills)    
        self.assertTrue(out.strip()=='C050: 26 F9           BNE     $C04B')

    def test_two_byte_relative(self):

        cp = opcodetools.cpu.cpu_manager.get_cpu_by_name('6809')
        binary = [0x10, 0x26, 0xDE, 0xAF]
        opc = cp.find_opcodes_for_binary(binary)[0]
        fills = cp.get_mnemonic_fills(opc, 0xC174, binary)

        out = cp.binary_to_string(opc, 0xC174, binary, fills)
        self.assertTrue(out.strip()=='C174: 10 26 DE AF     LBNE    $A027')
    

