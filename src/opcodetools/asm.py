import opcodetools.assembler.assembler_manager
import opcodetools.cpu.cpu_manager


filename = '../../test/test_assembler/DoubleGap.asm'

with open(filename) as f:
    lines = f.readlines()
    
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

lines = asm.load_lines(filename)
asm.lines = lines
asm.code = asm.remove_comments_and_blanks(lines)
asm.assemble()
asm.write_listing('test.lst')
asm.write_binary('test.bin')
