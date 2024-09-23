_start:

    add x1, x2, x3    
    sub x4, x5, x6    
    xor x7, x8, x9    
    or x10, x11, x12  
    and x13, x14, x15 
    jalr x5, 76(x2)

    sll x16, x17, x18 
    srl x19, x20, x21
    sra x22, x23, x24


    slt x25, x26, x27 
    sltu x28, x29, x30   

    addi x1, x2, 10
    andi x3, x4, 5     
    ori x5, x6, 15    
    xori x7, x8, 7 
              
label1:
    
    lb x9, 0(x10)        
    lh x11, 4(x12)       
    lw x13, 8(x14)       
    lbu x15, 12(x16)     
    lhu x17, 16(x18)
    sb x1, 0(x2)
    sh x3, 4(x4)
    sw x5, 8(x6)

    beq x7, x8, label1
    bne x9, x10, label2
    blt x11, x12, label3
    bge x13, x14, label1
    
label2:
    bltu x15, x16, label3
    bgeu x17, x18, label4

    jal x19, label4
    jalr x20, x21, 0

    lui x22, 0x1000
    auipc x23, 0x2000

    ecall

label3:
    la x3, 80000
    nop
    mv x1, x2
    not x1, x2
    neg x1, x2

label4:
    seqz x1, x2
    snez x1, x2
    sltz x1, x2
    sgtz x1, x2
    beqz x1, label1
    bnez x1, label1
    blez x1, label1
    bgez x1, label1
    bltz x1, label1
    bgtz x1, label1
    bgt x1, x2, label1
    ble x1, x2, label1
    bgtu x1, x2, label1
    bleu x1, x2, label1