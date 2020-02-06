from cpu.opcode import Opcode


class BaseDisassembly:

    def init_disassembly(self):
        pass

    def get_field_spacing(self):
        '''Return the field spacing for disassembly

        Returns:
            dict: spacing for parts of disassembly
        '''
        return {
            'address_size': 4,  # Number of digits
            'data': 16,  # Spacing reserved for the data section
            'mnemonic': [8, 20]  # Spacing for each part of the mnemonic
        }

    def binary_to_string(self, opcode: Opcode, address: int, binary: list, fills: dict):
        '''Make a disassembly string from the given info

        Args:
            opcode (Opcode): the opcode
            address (int): the address of the opcode
            binary (list): the opcode data
            fills (dict): the opcode fill-in information

        Returns:
            The complete disassembly string        
        '''

        # Spacing for the disassembly fields
        spa = self.get_field_spacing()

        # Address
        fs = '{:0' + str(spa['address_size']) + 'X}'
        add = fs.format(address)

        # Data
        ds = ''
        for i in range(len(binary)):
            ds = ds + '{:02X} '.format(binary[i])
        ds = ds.ljust(spa['data'], ' ')

        # Multi-word mnemonic spacing
        # TODO: use however many words are in the array ... or just the one if it isn't an array
        mn = opcode.mnemonic
        i = mn.find(' ')
        if i >= 0:
            a = mn[0:i]
            b = mn[i + 1:]
            mn = a.ljust(spa['mnemonic'][0]) + b.ljust(spa['mnemonic'][1])
        else:
            mn = mn.ljust(spa['mnemonic'][0] + spa['mnemonic'][1])

        # Build the basic form
        base = f'{add}: {ds}{mn}'

        for f in fills:
            fill_info = fills[f]
            i = base.find(f)
            if i >= 0:
                # TODO: visible spacing
                base = base.replace(f, fill_info['sub_value'])

        return base

    def binary_to_string_fill(self, address: int, binary: list, opcode: Opcode, fills: dict, ind: int):
        '''Fill in an opcode data value
        
        # TODO: clunky with the multi-byte values.

        Different processors might override this for their own special needs. The 
        "binary_to_string" defers to this method.

        Entries are added to fills for example:
            'p' : {
                'sub_value' : '$1024', # The actual value (string)
                'visual_size' : 5      # Number of printed characters in sub (might include HTML)
                'numeric_value' : 0    # Actual numeric value 
            }

        Args:
            address (int): the address of the opcode
            binary (list): the binary data for the opcode
            opcode (Opcode): the Opcode
            fills (dict): dictionary of fill-in values (add to this)            
            ind (int): bytes index of the fill-in (binary and opcode)

        '''
        # Find/make the fill-in entry
        spec = opcode.code[ind]
        if spec[0] not in fills:
            fills[spec[0]] = {'sub_value': '$00', 'visual_size': 3, 'numeric_value': 0}
            entry = fills[spec[0]]
        else:
            entry = fills[spec[0]]

        ov = entry['numeric_value']

        # New numeric value
        val = binary[ind]
        if spec[1] == '1':
            val = val * 256
            entry['visual_size'] = 5
        val += ov
        entry['numeric_value'] = val

        # New substitution string
        fs = '${:0' + str(entry['visual_size'] - 1) + 'X}'        

        if 'pcr' in opcode.use[spec[0]]:
            if 's1' in opcode.use[spec[0]]:
                # One byte relative (from start of next instruction)
                fa = address + len(opcode.code)
                if val<0x80:
                    fa = fa + val
                else:
                    fa = fa + (val - 256)                
            else:
                # TODO: support for more than s1,s2
                # Two byte relative (from start of next instruction)
                fa = address + len(opcode.code)
                if val<0x8000:
                    fa = fa + val
                else:
                    fa = fa + (val - 65536)
            entry['relative_target'] = fa
            val = fa
        
        entry['sub_value'] = fs.format(val)

    def get_mnemonic_fills(self, opcode: Opcode, address: int, binary: list):
        '''Get all the fill-in information for a given opcode

        Args:
            opcode (Opcode): the opcode
            address (int): the address of the opcode
            binary (list): the binary data for the opcode

        Returns:
            dict: all the fill ins
        '''

        code = opcode.code
        fills = {}
        for i in range(len(binary)):
            g = code[i]
            if isinstance(g, str):
                # Call out to the specific CPU in case it has specials
                self.binary_to_string_fill(address, binary, opcode, fills, i)

        return fills

    def find_opcodes_for_binary(self, binary: list, start: int=0, end: int=-1, exact: bool=False)->list:
        '''Find the opcodes that matches the binary (a disassembly operation)

        Args:
            binary (list[int]): the bytes to disassemble
            start (int): starting point in the bytes [default is 0]
            exact (bool): True if the opcode must match the given bytes exactly [default is False]
        Returns:
            list[Opcode]: The opcodes information 
        '''

        if end < 0:
            end = len(binary)

        possible = self._quick_codes[binary[0]]

        ret = []

        for oc in possible:
            if exact and len(oc.code) != (end - start):
                continue
            code = oc.code
            could_be = True
            for b in range(len(code)):
                if b >= end + start:
                    could_be = False
                    break
                if isinstance(code[b], str):
                    # Matches anything
                    continue
                if code[b] != binary[start + b]:
                    could_be = False
                    break
            if could_be:
                ret.append(oc)

        return ret
