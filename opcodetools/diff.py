import sys

with open(sys.argv[1],'rb') as f:
    d1 = f.read()

with open(sys.argv[2],'rb') as f:
    d2 = f.read()

if len(d1)!=len(d2):
    print('Different lengths')
else:
    for i in range(len(d1)):
        if d1[i]!=d2[i]:
            print("Different at",hex(i))