from opcodetools.assembler.assembler import Assembler, ASMException

import sys

# TODO: lots of command line options:
#  - Listing file (yes/no)
#  - Output file (name)

try:
    a = Assembler(sys.argv[1])
    a.assemble()
    a.write_binary(sys.argv[1] + '.bin')
    a.write_listing(sys.argv[1] + '.lst')
except ASMException as ex:
    print('##', str(ex))
    print('##', ex.line)
