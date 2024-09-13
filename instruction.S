label1:
la x3, 80000

label2:
add x1, x2, x3   # Suma
sub x4, x5, x6   # Resta
and x16, x17, x18 # AND
or x19, x20, x21  # OR
xor x22, x23, x24 # XOR
sll x25, x26, a5   # Shift left logical
srl x27, x28, s0   # Shift right logical
slt x29, x30, x31 # Set less than

label3:
beq x1, x2, label1   # Branch equal
bne x3, x4, label2   # Branch not equal
blt x5, x6, label3   # Branch less than
bge x7, x8, label4   # Branch greater than or equal
jal x4, label1           # Jump and link
jalr x1, 0(x9)      # Jump and link register

label4:
auipc x4, 100   # Add upper immediate to PC
lui x5, 200     # Load upper immediate

label5:
addi x29, x28, 0x10
nop
seqz x5, x3
la x3, 345
sb x4, 76, x2
call label4