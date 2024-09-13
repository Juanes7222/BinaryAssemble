from values import INSTRUCTIONS_FILE, LABELS, EQUIVALENCES, PSEUDOINSTRUCTIONS_FILE, BINARY_INSTRUCTIONS
from functools import singledispatch
from bitstring import Bits, BitArray
import json
import re

def get_instructions_info(file):
    with open(file, "r") as f:
        info = json.load(f)
    return info

INFO: dict = get_instructions_info(INSTRUCTIONS_FILE)
PSEUDOINSTRUCTIONS: dict = get_instructions_info(PSEUDOINSTRUCTIONS_FILE)

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
    binary = int(number).to_bytes(length=5, signed=True)
    normal_binary = ''.join(format(byte, '08b') for byte in binary)
    return normal_binary[-length:]

def bin_to_decimal(binary: str):
    bin = Bits(bin=binary)
    return bin.int

def get_number(reg):
    return int(re.search(r'\d+', reg).group())

def registers(reg):
    if not "x" in reg:
        x_reg = EQUIVALENCES.get(reg)
        if not x_reg:
            raise ValueError(f"Invalid register: {reg}")
        reg = x_reg
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
    label = number_to_binary(label, 13)
    
    operation = instruction["operation"]
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

def distance_label(label, line):
    label_line = LABELS.get(label, "False")
    if isinstance(label_line, int):
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
        if inst == "jalr":
            return [INFO["I2"], INFO["I3"]], t_inst
        return INFO[t_inst], t_inst
    else:
        label = confirm_label(inst)
        if not label:
            match, equivalence = is_pseudo(instruction)
            if match != None:
                compile_pseudo(equivalence, match, line)
            else:
                raise ValueError(f"Invalid instruction: {instruction} --> Line: {line}")
    return None, None

def get_all_labels(instructions: list):
    i = 0
    for instruction in instructions.copy():
        label = confirm_label(instruction)
        if label:
            LABELS[label] = i
            i -= 1
            instructions.remove(instruction)
        i += 1
        
def is_pseudo(instruction: str):
    for pattern, equivalence in PSEUDOINSTRUCTIONS.items():
        match = re.match(fr"{pattern}", instruction)
        if match:
            return match.groupdict(), equivalence
    return False, False

def cut_symbol(symbol: str, line=None):
    try:
        symbol = distance_label(symbol,line)
    except ValueError:
        pass
        # if "0x" in symbol:
        #     symbol = int(symbol, 16)
        # else:
        #     symbol = int(symbol)
    symbol = BitArray(uint=int(symbol), length=32)
    print(symbol.int)
    symbol <<= 12
    # symbol = number_to_binary(symbol, 32)
    new_symbol = {
        "symbol1": bin_to_decimal(symbol.bin[:20]),
        "symbol2": bin_to_decimal(symbol.bin[:12]),
    }
    # mask = (1 << 12) - 1
    # new_symbol = {
    #     "symbol1": symbol >> 20,
    #     "symbol2": symbol & mask,
    # }
    return new_symbol

@singledispatch
def compile_pseudo(equivalence: str, match: dict, line: str|int):
    equivalence = equivalence.format(**match)
    binary = instruction_manager(equivalence, line)
    BINARY_INSTRUCTIONS.append(binary)

@compile_pseudo.register
def _(equivalence: list, match: dict, line: str|int):
    equivalence = "|".join(equivalence)
    match.update(cut_symbol(match["symbol"], line))
    del match["symbol"]
    equivalence = equivalence.format(**match)
    for eq in equivalence.split("|"):
        binary = instruction_manager(eq, line)
        BINARY_INSTRUCTIONS.append(binary)

def special_instruction(instruction, info_instructions):
    for i, info in enumerate(info_instructions):
        re = regular_expression(info["inst"].keys(), info["re"])
        try:
            token_instruction = tokenize(instruction, re)
            return token_instruction, i
        except ValueError:
            pass

def compile_instruction(token_instruction, info, t_inst, line):
    if t_inst == "R":
        binary = r_instruction(token_instruction, info)
    elif t_inst == "I1" or t_inst == "I2" or t_inst == "I3":
        binary = i_instruction(token_instruction, info)
    elif t_inst == "S":
        binary = s_instruction(token_instruction, info)
    elif t_inst == "B":
        binary = b_instruction(token_instruction, info, line)
    elif t_inst == "U":
        binary = u_instruction(token_instruction, info)
    elif t_inst == "J":
        binary = j_instruction(token_instruction, info, line)
    return binary

def instruction_manager(instruction, line):
    info, t_inst = get_info(instruction, line)
    if info:
        if isinstance(info, list):
            token_instruction, i = special_instruction(instruction, info)
            info = info[i]
        else:
            re = regular_expression(info["inst"].keys(), info["re"])
            try:
                token_instruction = tokenize(instruction, re)
            except ValueError as e:
                match, equivalence = is_pseudo(instruction)
                if match:
                    compile_pseudo(equivalence, match, line)
                    return
                else:
                    raise e
        binary = compile_instruction(token_instruction, info, t_inst, line)
        # print(token_instruction, binary)
        return binary

def clean_instructions(instructions: str):
    result = re.sub(r'#.*$', '', instructions, flags=re.MULTILINE)
    return result
    
def main(file):
    instructions_file = read_file(file)
    instructions_file = clean_instructions(instructions_file)
    instructions = sep_lines(instructions_file)
    get_all_labels(instructions)
    
    for line, instruction in enumerate(instructions, 0):
        binary = instruction_manager(instruction, line)
        if binary:
            BINARY_INSTRUCTIONS.append(binary)

def valid(binary_instructions: list[str]):
    for i, element in enumerate(binary_instructions):
        binary = element[0].replace("-", "")
        if len(binary) != 32:
            print(f"Instruccion invalida: {i}\nBinario: {element[0]} Instruccion: {element[1]} len:{len(element[0])}")
# print(Bits(bin="100010000000").int)
print(number_to_binary("3294967296", 32))
main("./instruction.S")
print(BINARY_INSTRUCTIONS)
# valid(binary_instructions)

values = ['00000000000000010000000010000011', '11111111110000100001000110000011', '00000000100000110010001010000011', '00000000110001000100001110000011', '00000001000001010101010010000011', '11111110101101100000011000100011', '00000000110101110001110000100011', '00000000111110000010111000100011', '00000000001100010000000010110011', '01000000011000101000001000110011', '00000001001010001111100000110011', '00000001010110100110100110110011', '00000001100010111100101100110011', '00000000111111010001110010110011', '00000000100011100101110110110011', '00000001111111110010111010110011', '11111100001000001000000011100011', '11111100010000011001111011100011', '11111110011000101100110011100011', '00000000100000111101011001100011', '11111011000111111111001001101111', '00000000000001001000000011100111', '00000000000001100100001000010111', '00000000000011001000001010110111', '00000001000011100000111010010011']

# for value, binary in zip(values, binary_instructions):
#     if value != binary[0]:
#         print(f"Diferent value: {binary[0]}\nExpected: \t\t{value}\nInstruction: {binary[1]}")
        
#TODO: verificar como se hacen la instruccion "jalr"