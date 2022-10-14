import sys

from opcodetools.utils import binary
from opcodetools.cpu import cpu_manager

arg_parse = sys.argv

# py dasm Z80 1000 "a.bin+b.bin+c.bin"
#arg_parse = ['','Z80GB','0','d:/git/gbc-sea-hunt/dmg_boot.bin']
#arg_parse = ['','6809','C000','d:/git/computerarcheology/content/coco/doubleback/roms/doubleback.bin']
#arg_parse = ['','6809','8000','d:/git/computerarcheology/content/arcade/digdug2/roms/main.bin']
arg_parse = ['','6809','E000','d:/git/computerarcheology/content/arcade/digdug2/roms/sound.bin']

cpuname = arg_parse[1]
org = int(arg_parse[2], 16)
names = arg_parse[3]

bindata = binary.load_binary(names)

cpu = cpu_manager.get_cpu_by_name(cpuname)

print('; CPU:', cpuname)
print('; ORIGIN:', hex(org))
print('; FILES:', names)
print()

pos = 0

while pos < len(bindata):
    ops = cpu.find_opcodes_for_binary(bindata[pos:])
    if len(ops) != 1:
        print(cpu.binary_to_string_unknown(pos + org, bindata[pos]))
        pos += 1
        continue

    opc = ops[0]

    dat = bindata[pos:pos + len(opc.code)]
    fills = cpu.get_mnemonic_fills(ops[0], dat, pos + org)
    s = cpu.binary_to_string(opc, dat, pos + org, fills)
    pos += len(dat)

    print(s)
