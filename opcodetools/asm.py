from opcodetools.assembler.assembler import Assembler, ASMException

import sys
import os

# TODO: lots of command line options:
#  - Listing file (yes/no)
#  - Output file (name)

try:
    a = Assembler(sys.argv[1])
    a.assemble()
    a.write_binary(sys.argv[1] + '.bin')
    a.write_listing(sys.argv[1] + '.lst')
    a.write_labels(sys.argv[1] + '.lab.asm')
except ASMException as ex:
    print('##', str(ex))
    print('##', ex.line)
