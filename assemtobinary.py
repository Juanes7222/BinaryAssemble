import json
import re

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
    list_text = text.split("\n")
    return list(filter(None, list_text))

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
    pattern = re.compile(fr"{expression}")
    match_instruction = pattern.match(instruction)
    if match_instruction:        
        return match_instruction.groupdict()
    else:
        raise ValueError(f"Invalid instruction: {instruction}")

def number_to_binary(number: int | str, length=4):
    if isinstance(number, str):
        if "0x" in number:
            number = int(number, 16)
    binary = int(number).to_bytes(length=4, signed=True)
    normal_binary = ''.join(format(byte, '08b') for byte in binary)
    return normal_binary[-length:]

def get_number(reg):
    return int(re.search(r'\d+', reg).group())

def registers(reg):
    num_reg = get_number(reg)
    return number_to_binary(num_reg, 5)

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
    label = number_to_binary(label, 12)
    
    operation = instruction["operation"]
    funct3 = info["inst"][operation]["funct3"]
    opcode = info["opcode"]
    
    binary = f"{label[0]}{label[2:8]}{rs2}{rs1}{funct3}{label[8:]}{label[1]}{opcode}"
    
    return binary

def j_instruction(instruction: dict, info):
    label = instruction["label"]
    line_label = LABELS[label]
    label = number_to_binary(line_label, 20)
    
    rd = instruction["rd"]
    rd = registers(rd)
    
    opcode = info["opcode"]
    
    binary = f"{label[0]}{label[10:]}{label[9]}{label[1:9]}{rd}{opcode}"
    return binary

def distance_label(label, line):
    label_line = LABELS.get(label)
    if label_line:
        distance = label_line - line
        return distance*4
    raise ValueError(f"Invalid Label: {label} --> Line: {line}")

def confirm_label(label):
    match = re.findall(r"(\w+):", label)
    if match:
        return match[0]
    
def get_info(instruction, line=None):
    inst = get_instruction(instruction)
    t_inst = type_instruction(inst)
    if t_inst:
        return INFO[t_inst], t_inst
    else:
        label = confirm_label(inst)
        if not label:
            raise ValueError(f"Invalid instruction: {instruction} --> Line: {line}")
    return None, None

def get_all_labels(instructions: str):
    for i, instruction in enumerate(instructions, 1):
        label = confirm_label(instruction)
        if label:
            LABELS[label] = i+1

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
    get_all_labels(instructions)
    binary_instructions = []
    
    for line, instruction in enumerate(instructions, 1):
        binary = instruction_manager(instruction, line)
        if binary:
            binary_instructions.append([binary, instruction])
    return binary_instructions

def valid(binary_instructions: list[str]):
    for i, element in enumerate(binary_instructions):
        binary = element[0].replace("-", "")
        if len(binary) != 32:
            print(f"Instruccion invalida: {i}\nBinario: {element[0]} Instruccion: {element[1]} len:{len(element[0])}")

valid(main("./instruction.rsv"))

values = ["00000000000000000000001011101111", "00000000100000000000001011101111",
          ]
            
#TODO: corregir las expresiones regulares referentes a los imm() y terminar de validar