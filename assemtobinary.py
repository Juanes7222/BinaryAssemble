import json
import re

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
        if instruction in data.keys():
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

def decimal_to_binary(number, lenght=4):
    # binary = bin(int(number))
    binary = format(int(number), f"0{lenght}b")
    return binary

def get_number(reg):
    return re.search(r'\d+', reg).group()

def r_instruction(instruction: dict, info):
    rd = instruction["rd"]
    rd = get_number(rd)
    rd = decimal_to_binary(rd)
    
    rs1 = instruction["rs1"]
    rs1 = get_number(rs1)
    rs1 = decimal_to_binary(rs1)
    
    rs2 = instruction["rs2"]
    rs2 = get_number(rs2)
    rs2 = decimal_to_binary(rs2)
    
    operation = instruction.get("operation")
    
    func3 = info["inst"][operation]["funct3"]
    func7 = info["inst"][operation]["funct7"]
    opcode = info["opcode"]
    
    binary = f"{func7}{rs2}{rs1}{func3}{rd}{opcode}"
    
    return binary

def i_instruction(instruction: dict, info):
    ...
    
def b_instruction():...
def u_instruction():...
def j_instruction():...
def s_instruction():...

def distance_label(label, line):
    label_line = LABELS.get(label)
    if label_line:
        distance = label_line - line
        return distance*4
    raise Exception(f"Invalid Label: {label}")

def confirm_label(label):
    match = tokenize(label, "?P<label>\w+:")
    label_name = match.get("label")
    if label_name:
        return label_name    

def get_info(instruction, line=None):
    inst = get_instruction(instruction)
    t_inst = type_instruction(inst)
    if t_inst:
        return INFO[t_inst]
    else:
        label = confirm_label(inst)
        if label:
            LABELS[label] = line+1
        else:
            raise ValueError(f"Invalid instruction: {instruction} --> Line: {line}")

# TODO: terminar la funcion del main y las instrucciones

def main(instruction):...

info = INFO["I"]
expr = regular_expression(info, )
inst = tokenize("addi s3, s2, 12", info)
print(inst)

# print(r_instruction(inst, info))