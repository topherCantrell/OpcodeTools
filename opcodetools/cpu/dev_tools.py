
import cpu_6502,cpu_6803,cpu_6809,cpu_Z80,cpu_Z80GB,cpu_8052,cpu_DVG

check = [
    ('6502',    cpu_6502.OPCODES), 
    ('6803',    cpu_6803.OPCODES),
    ('6809Ops', cpu_6809.OPCODES),
    ('6809Pst', cpu_6809.POSTS),
    ('Z80',     cpu_Z80.OPCODES),
    ('Z80GB',   cpu_Z80GB.OPCODES),    
    ('8502',    cpu_8052.OPCODES),
    ('DVG',     cpu_DVG.OPCODES),
]

def list_uses(check):
    terms = []
    for name,ops in check:
        for m in ops:            
            u = m['use']
            if u:                
                us = u.split(',')
                #print(us)
                for ust in us:
                    if ust.startswith('y_'):
                        # 6809 post field
                        continue
                    _,v = ust.split('=')
                    if v not in terms:
                        terms.append(v)    
    for t in terms:
        print(t)                       

def list_multi_fills(check):
    for name,ops in check:
        for m in ops:
            u = m['use']
            if u:
                us = u.split(',')
                if len(us)>1:
                    print(name,':',m) 

list_uses(check)
list_multi_fills(check)