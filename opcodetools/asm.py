from opcodetools.assembler.assembler import Assembler, ASMException

import sys
import os

# asm test.asm -o test.bin -l test.lst -m test.lab.asm -d value=0x71

a,b = sys.argv[1].split('.')
bin_name = a+".bin"
lst_name = None
lab_name = None
defines = {}
for i in range(2, len(sys.argv)):
    if sys.argv[i].startswith('-o'):
        bin_name = sys.argv[i+1]
        i+=1
    elif sys.argv[i].startswith('-l'):
        lst_name = sys.argv[i+1]
        i+=1
    elif sys.argv[i].startswith('-m'):
        lab_name = sys.argv[i+1]
        i+=1
    elif sys.argv[i].startswith('-d'):
        key, value = sys.argv[i+1].split('=')
        defines[key] = int(value, 0)
        i+=1

try:
    a = Assembler(sys.argv[1], defines)
    a.assemble()

    a.write_binary(bin_name) 

    if lst_name:          
        a.write_listing(lst_name)

    if lab_name:
        a.write_labels(lab_name)      
    
except ASMException as ex:
    print('##', str(ex))
    print('##', ex.line)
