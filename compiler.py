from utils import registers, number_to_binary, distance_label

def r_instruction(instruction: dict, info):
    rd = instruction["rd"]
    rd = registers(rd)
    
    rs1 = instruction["rs1"]
    rs1 = registers(rs1)
    
    rs2 = instruction["rs2"]
    rs2 = registers(rs2)
    
    operation = instruction.get("operation")
    
    func3 = info["inst"][operation]["funct3"]
    func7 = info["inst"][operation]["funct7"]
    opcode = info["opcode"]
    
    binary = f"{func7}{rs2}{rs1}{func3}{rd}{opcode}"
    
    return binary

def i_instruction(instruction: dict, info):
    rd = instruction["rd"]
    rd = registers(rd)
    
    rs1 = instruction["rs1"]
    rs1 = registers(rs1)
    
    imm = instruction["imm"]
    imm = number_to_binary(imm, 12)
    operation = instruction["operation"]
    
    opcode = info["inst"][operation]["opcode"]
    funct3 = info["inst"][operation]["funct3"]
    
    binary = f"{imm}{rs1}{funct3}{rd}{opcode}"
    if operation == "srai":
        binary[1] = "1"
    return binary
    
def s_instruction(instruction: dict, info):
    rs1 = instruction["rs1"]
    rs1 = registers(rs1)
    
    rs2 = instruction["rs2"]
    rs2 = registers(rs2)
    
    imm = instruction["imm"]
    imm = number_to_binary(imm, 12)
    
    operation = instruction["operation"]
    funct3 = info["inst"][operation]["funct3"]
    opcode = info["opcode"]
    binary = f"{imm[0:7]}{rs2}{rs1}{funct3}{imm[7:]}{opcode}"
    
    return binary

def u_instruction(instruction: dict, info):
    imm = instruction["imm"]
    imm = number_to_binary(imm, 20)
    
    rd = instruction["rd"]
    rd = registers(rd)
    operation = instruction["operation"]
    opcode = info["inst"][operation]["opcode"]
    
    binary = f"{imm}{rd}{opcode}"
    
    return binary
    
    
def b_instruction(instruction: dict, info, line):
    rs1 = instruction["rs1"]
    rs1 = registers(rs1)
    
    rs2 = instruction["rs2"]
    rs2 = registers(rs2)
    
    label = instruction["label"]
    label = distance_label(label, line)
    
    operation = instruction["operation"]
        
    label = number_to_binary(label, 13)
    funct3 = info["inst"][operation]["funct3"]
    opcode = info["opcode"]
    
    binary = f"{label[0]}{label[2:8]}{rs2}{rs1}{funct3}{label[8:12]}{label[1]}{opcode}"
    
    return binary

def j_instruction(instruction: dict, info, line):
    label = instruction["label"]
    label = distance_label(label, line)
    label = number_to_binary(label, 21)
        
    rd = instruction["rd"]
    rd = registers(rd)
    
    opcode = info["opcode"]
    
    binary = f"{label[0]}{label[10:20]}{label[9]}{label[1:9]}{rd}{opcode}"
    return binary