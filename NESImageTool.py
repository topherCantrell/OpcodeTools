
def doAsmTool(asm,line,pass_num,block):    
    if not pass_num:
        line['data'] = [0]*16
        return
    
    plane0 = [0,0,0,0,0,0,0,0]
    plane1 = [0,0,0,0,0,0,0,0]

    for row in range(8):
        bn = 128
        for col in range(8):            
            if block[row][col] == '3':                
                plane0[row] = plane0[row]+bn
                plane1[row] = plane1[row]+bn
            elif block[row][col] == '1':                
                plane0[row] = plane0[row]+bn
            elif block[row][col] == '2':                
                plane1[row] = plane1[row]+bn
            bn >>= 1

    line['data'] = plane0 + plane1
    