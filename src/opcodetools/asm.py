import opcodetools.assembler.assembler_manager
import opcodetools.cpu.cpu_manager
import sys
import os

# TODO: this should come from command line
#filename = '../../test/test_assembler/DoubleGap.asm'
#filename = '../../test/test_assembler/test8052.asm'

filename = os.path.abspath(sys.argv[1])
basename = os.path.basename(filename)
basepath = os.path.dirname(filename)

i = basename.index('.')
lstname = os.path.join(basepath,basename[0:i]+'.lst')
binname = os.path.join(basepath,basename[0:i]+'.bin')

# Look for the CPU define if it wasn't given on the command line
with open(filename) as f:
    lines = f.readlines()
    
# Get the CPU and Assembler
cp = None
for line in lines:
    if line.strip().startswith('._CPU'):
        i = line.find(';')
        if i>=0:
            line = line[0:i]
        line = line.strip()
        i = line.find('=')
        if i>=0:
            name = line[i+1:].strip()
            cp = opcodetools.cpu.cpu_manager.get_cpu_by_name(name)        
            asm = opcodetools.assembler.assembler_manager.get_assembler_by_name(name)
        break

# Load the lines and strip the code
lines = asm.load_lines(filename)
asm.lines = lines
asm.code = asm.remove_comments_and_blanks(lines)

# Assemble the code
asm.assemble()

# Write the output
asm.write_listing(lstname)
asm.write_binary(binname)
