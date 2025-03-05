main:
        jal x1, main
        beqz x1, label1
        bnez x1, label1
        blez x1, label1
        bgez x1, label1
        bltz x1, label1
        bgtz x1, label1
        bgt x3, x4, label1
        ble x3, x4, label1
        bgtu x3, x4, label1
        bleu x3, x4, label1
        li t0, 125464
        mv t1, t0 
        not t2, t0       
        neg t3, t0       
        seqz x1, x3
        snez x1, x3
        sltz x1, x3
        sgtz x1, x3
        j label1
        call function
        jal function
        jr x3
        jalr x4
        tail function
function:
  ret
label1:
        addi    sp,sp,-32
        sw      ra,28(sp)
        sw      s0,24(sp)
        addi    s0,sp,32
        sw      a5,-20(s0)
        sw      a5,-24(s0)
        lw      a4,-28(s0)
        lw      a5,-24(s0)
        add     a5,a4,a5
        lw      ra,28(sp)
        lw      s0,24(sp)
        addi    sp,sp,32
sum:
        addi    sp,sp,-32
        sw      ra,28(sp)
        sw      s0,24(sp)
        addi    s0,sp,32
        sw      a0,-20(s0)
        sw      a1,-24(s0)
        lw      a4,-20(s0)
        lw      a5,-24(s0)
        add     a5,a4,a5
        mv      a0,a5
        lw      ra,28(sp)
        lw      s0,24(sp)
        addi    sp,sp,32
        jr      ra
label2:
        addi    sp,sp,-32
        sw      ra,28(sp)
        sw      s0,24(sp)
        addi    s0,sp,32
        li      a5,42
        sw      a5,-20(s0)
        lw      a5,-20(s0)
        neg     a5,a5
        sw      a5,-24(s0)
        lw      a5,-20(s0)
        not     a5,a5
        sw      a5,-28(s0)
        lw      a4,-20(s0)
        lw      a5,-24(s0)
        ble     a4,a5,L4
        lw      a5,-20(s0)
        j       L5
L4:
        lw      a1,-28(s0)
        lw      a0,-20(s0)
        call    sum
        li      a5,0
L5:
        mv      a0,a5
        lw      ra,28(sp)
        lw      s0,24(sp)
        addi    sp,sp,32
        jr      ra