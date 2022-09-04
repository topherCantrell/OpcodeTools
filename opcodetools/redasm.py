

args = ['','../../computerarcheology/content/coco/doubleback/code.md','test.txt']

def line_to_data(line):

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

with open(args[1]) as f:
    lines = f.readlines()

for line in lines:
    org,data = line_to_data(line)
    print(org,data)