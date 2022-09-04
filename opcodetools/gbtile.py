def art_to_tiles(text):    

    char_map = {}

    m = text[0]
    m = m[1:].split()
    for ent in m:
        k,v = ent.split('=')
        char_map[k] = v
    
    data = []
    for t in text[1:]:
        t=t.replace(' ','')
        if t:
            data.append(t)
    
    ret = []
    for row in range(0,len(data),8):        
        for col in range(0,len(data[row]),8):
            tile = ''
            for i in range(8):
                tile = tile + data[row+i][col:col+8]
            ret.append(tile)
    return char_map, ret

def tiles_to_data(tiles,palette):
    ret = []    

    for tile in tiles:
        for i in range(0,64,8):
            g = tile[i:i+8]            
            for k,v in palette.items():
                g = g.replace(k,v)
            g = g.replace('.','00')
            g = g.replace('1','01') # Replace "1" before any others that contain "1"
            g = g.replace('2','10')
            g = g.replace('3','11')                
            a = ''
            b = ''
            for i in range(0,16,2):
                a = a + g[i]
                b = b + g[i+1]
            a = int(a,2)
            b = int(b,2)
            
            ret.append(b)
            ret.append(a)    
    return ret

def doAsmTool(assembler,line,pass_number,text):
    # TODO lots of error checking
    if pass_number>=1:
        # We only need the first pass
        return    

    palette,tiles = art_to_tiles(text)    

    line['data'] = tiles_to_data(tiles,palette)
    
    
def unique_and_map(assembler,line,pass_number,text):
    global last_map
    if pass_number>=1:
        # We only need the first pass
        return 

    palette,tiles = art_to_tiles(text)    
    
    map = []
    uniques = []
    for t in tiles:
        if t not in uniques:
            uniques.append(t)
        map.append(uniques.index(t))

    line['data'] = tiles_to_data(tiles,palette)
    last_map = map

def map(assembler,line,pass_number,text):
    if pass_number>=1:
        # We only need the first pass
        return 
    line['data'] = last_map
