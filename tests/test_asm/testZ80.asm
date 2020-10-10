; Example assembly input

;.include hardware.asm

._CPU = Z80
.CONST_A = 0x20

0x8000:
Start:

   LD  A,0x23     ; constant
   LD  A,(0x10)   ; memory location
   LD  HL,(DataB) ; memory location
   LD  HL,DataA   ; constant
   LD  E,CONST_A  ; constant
   JP  Start

DataA:
. 0x10,0x20,0x30

DataB:
.word 0x1234
