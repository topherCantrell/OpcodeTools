
class CodeLine:

    def __init__(self,text):
        # hold the original text
        self.original = text        

        self.text = None
        self.address = None
        self.data = None
        self.mnemonic = None
        self.comment = None

        # parse out comment
        i = text.find(';')
        if i>=0:
            self.comment = text[i+1:].strip()
            text = text[:i].strip()        
        if text.find(':')!=4:
            self.text = text
        else:
            # parse out address
            self.address = int(text[0:4],16)            
            text = text[5:].strip()
            # parse out data
            self.data = []
            while True:
                if len(text) < 2:
                    break
                if len(text) > 2 and text[2] != ' ':
                    break
                try:
                    val = int(text[0:2], 16)
                except ValueError:
                    break
                self.data.append(val)
                text = text[2:].strip()
            # parse out mnemonic        
            self.mnemonic = text
    
    def __repr__(self):
        return f':{self.address}:{self.data}:{self.mnemonic}:{self.comment}:{self.text}:'

def load_code_lines(name):
    lines = []
    with open(name) as f:
        for g in f:       
            c = CodeLine(g.strip())
            if c.text:
                lines.append(c)
    return lines

# load_code_lines('../computerarcheology/content/coco/doubleback/code.md')  