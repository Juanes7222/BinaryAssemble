hola:
        j hola
suma(int, int):
        lw      s0,24(sp)
        addi    sp,sp,32
        jr      ra
main:
        j       .L4
.L5:
        lw      a4,-24(s0)
        lw      a5,-20(s0)
        mul     a5,a4,a5
        sw      a5,-24(s0)
        lw      a5,-20(s0)
        addi    a5,a5,-1
        sw      a5,-20(s0)
.L4:
        lw      a4,-20(s0)
        li      a5,1
        bgt     a4,a5,.L5
        lw      a5,-24(s0)
        mv      a0,a5
        lw      ra,28(sp)
        lw      s0,24(sp)
        addi    sp,sp,32
        jr      ra