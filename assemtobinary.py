import json
import re
import sys
# "(expr)\\s+(?P<rd>\\w+),\\s*((?P<rs1>(\\w+))|(?P<imm>([+-]?\\d+\\(?P<rs1>(\\w+)\\))))?(,)?\\s*(?P<imm>[+-]\\d+)?$"


INSTRUCTIONS_FILE = "./instructions_info.json"
LABELS = {}

def get_instructions_info():
    with open(INSTRUCTIONS_FILE, "r") as f:
        info = json.load(f)
    return info

INFO: dict = get_instructions_info()

def read_file(file):
    with open(file, "r", encoding="utf-8") as f:
        text_file = f.read()
    return text_file

def sep_lines(text: str):
    return text.split("\n")

def get_instruction(instruction: str):
    inst_sep = instruction.split(" ")
    return inst_sep[0]

def type_instruction(instruction):
    for type_i, data in INFO.items():
        if instruction in data["inst"].keys():
            return type_i       

def regular_expression(instrs: list, expression: str):
    instructions = "|".join(instrs)
    return expression.replace("expr", f"?P<operation>{instructions}")

def tokenize(instruction, expression):
    # expression = regular_expression(info)
    pattern = re.compile(fr"{expression}")
    match_instruction = pattern.match(instruction)
    if match_instruction:        
        return match_instruction.groupdict()
    else:
        raise ValueError(f"Invalid instruction: {instruction}")

def decimal_to_binary(number: int | str, length=4):
    binary = int(number).to_bytes(length=4, signed=True)
    normal_binary = ''.join(format(byte, '08b') for byte in binary)
    # print(normal_binary)
    return normal_binary[-length:]

def get_number(reg):
    return int(re.search(r'\d+', reg).group())

def registers(reg):
    num_reg = get_number(reg)
    return decimal_to_binary(num_reg, 5)

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
    
    binary = f"{func7}-{rs2}-{rs1}-{func3}-{rd}-{opcode}"
    
    return binary

def i_instruction(instruction: dict, info):
    rd = instruction["rd"]
    rd = registers(rd)
    
    rs1 = instruction["rs1"]
    rs1 = registers(rs1)
    
    imm = instruction["imm"]
    imm = decimal_to_binary(imm, 12)
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
    imm = decimal_to_binary(imm)
    
    operation = instruction["operation"]
    funct3 = info["inst"][operation]["funct3"]
    opcode = info["inst"]["opcode"]
    binary = f"{imm[5:11]}{rs2}{funct3}{imm[0:4]}{opcode}"
    
    return binary

def u_instruction(instruction: dict, info):
    imm = instruction["imm"]
    imm = decimal_to_binary(imm, 20)
    
    rd = instruction["rd"]
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
    label = decimal_to_binary(label, 12)
    
    operation = instruction["operation"]
    funct3 = info["inst"][operation]["funct3"]
    opcode = info["opcode"]
    
    binary = f"{label[0]}{label[2:7]}{rs2}{rs1}{funct3}{label[8:11]}{label[1]}{opcode}"
    
    return binary

def j_instruction():...

def distance_label(label, line):
    label_line = LABELS.get(label)
    if label_line:
        distance = label_line - line
        return distance*4
    raise ValueError(f"Invalid Label: {label} --> Line: {line}")

def confirm_label(label):
    match = tokenize(label, "?P<label>\\w+:")
    label_name = match.get("label")
    if label_name:
        return label_name    

def get_info(instruction, line=None):
    inst = get_instruction(instruction)
    t_inst = type_instruction(inst)
    if t_inst:
        return INFO[t_inst], t_inst
    else:
        label = confirm_label(inst)
        if label:
            LABELS[label] = line+1
        else:
            raise ValueError(f"Invalid instruction: {instruction} --> Line: {line}")
    return None, None

def instruction_manager(instruction, line):
    info, t_inst = get_info(instruction, line)
    if info:
        re = regular_expression(info["inst"].keys(), info["re"])
        token_instruction = tokenize(instruction, re)
        if t_inst == "R":
            binary = r_instruction(token_instruction, info)
        elif t_inst == "I1" or t_inst == "I2":
            binary = i_instruction(token_instruction, info)
        elif t_inst == "S":
            binary = s_instruction(token_instruction, info)
        elif t_inst == "B":
            binary = b_instruction(token_instruction, info, line)
        elif t_inst == "U":
            binary = u_instruction(token_instruction, info)
        elif t_inst == "J":
            binary = j_instruction(token_instruction, info)
            
        return binary

def main(file):
    instructions_file = read_file(file)
    instructions = sep_lines(instructions_file)
    binary_instructions = []
    
    for line, instruction in enumerate(instructions, 1):
        binary = instruction_manager(instruction, line)
        binary_instructions.append(binary)
    return binary_instructions

print(main("./instruction.rsv"))
            
#TODO: corregir las expresiones regulares referentes a los imm() y terminar de validar