from typing import List

# TODO we need an object representing a line of disassembly and its parts (address, data, mnemonic, comment)
# TODO then a function to parse that
# TODO then the line_to_data and extract functions take one of these

def load_disassembly(lines):
    if type(lines) == str:
        with open(lines) as f:
            lines = []
            for s in f:
                lines.append(f.readline()[:-1])

    # address
    # data
    # mnemonic
    # comment
    
    print(lines)

def extract_data_from_disassembly(lines:List[str]):
    pass

def line_to_data(line):
    """Extract data from disassembly line

    Args:
        line(str) : The line of disassembly
    Returns:
        tuple(int,list[int]) : The origin and list of bytes (None, None) if not mnemonic
    """

    if ';' in line:
        line = line[0:line.index(';')]

    line = line.strip()

    if len(line) < 5:
        return None, None

    if line[4] != ':':
        return None, None

    try:
        org = int(line[0:4], 16)
    except ValueError:
        return None, None

    line = line[5:].strip()
    ret = bytearray()

    while True:
        if len(line) < 2:
            break
        if len(line) > 2 and line[2] != ' ':
            break
        try:
            val = int(line[0:2], 16)
        except ValueError:
            break
        ret.append(val)
        line = line[2:].strip()

    return org, ret

def load_binary(names: str) -> List[int]:
    """Read a group of binary files

    For example "a.bin + b.bin + c.bin"

    Args:
        names (str) : the group of names
    Returns:
        List[int] : the binary data
    """

    # TODO origins on each file

    names = names.split('+')
    ret = []
    for n in names:
        n = n.strip()
        with open(n, 'rb') as f:
            data = f.read()
            for d in data:
                ret.append(int(d))

    return ret
