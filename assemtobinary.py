import json
import re

INSTRUCTIONS_FILE = "./instructions_info.json"

def get_instructions_info():
    with open(INSTRUCTIONS_FILE, "r") as f:
        info = json.load(f)
    return info

INFO = get_instructions_info() 
def read_file(file):
    with open(file, "r", encoding="utf-8") as f:
        text_file = f.read()
    return text_file

def sep_lines(text: str):
    return text.split("\n")

def regular_expression(info):
    instructions = "|".join(info["inst"])
    return info["stmt"].replace("expr", f"?P<operation>{instructions}")

def tokenize(expr, info):
    expression = regular_expression(info)
    pattern = re.compile(fr"{expression}")
    match_instruction = pattern.match(expr)
    if match_instruction:        
        return match_instruction.groupdict()
    else:
        raise ValueError(f"Invalid instruction: {expr}")

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

info = INFO["R"]
inst = tokenize("add s3, s2, s4", info)

print(r_instruction(inst, info))