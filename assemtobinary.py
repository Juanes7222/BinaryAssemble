from values import INSTRUCTIONS_FILE, BINARY_INSTRUCTIONS, LABELS
from functools import singledispatch
from utils import get_instructions_info, read_file, sep_lines, confirm_label, is_pseudo, cut_symbol, values_prepare
from compiler import r_instruction, i_instruction, b_instruction, u_instruction, s_instruction, j_instruction
from files import push_info
import re

INFO: dict = get_instructions_info(INSTRUCTIONS_FILE)

def get_info(instruction, line=None):
    inst = get_instruction(instruction.strip())
    t_inst = type_instruction(inst)
    
    if t_inst:
        if inst == "jalr":
            return [INFO["I2"], INFO["I3"]], t_inst
        return INFO[t_inst], t_inst
    else:
        label = confirm_label(inst)
        if not label:
            raise ValueError(f"Invalid instruction: {instruction} --> Line: {line}")
        
    return None, None

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

@singledispatch
def compile_pseudo(equivalence: str, match: dict, line: str|int):
    equivalence = equivalence.format(**match)
    return [equivalence]
  
@compile_pseudo.register
def _(equivalence: list, match: dict, line: str|int):
    equivalence = "|".join(equivalence)
    symbols = cut_symbol(match["symbol"], line)
    if symbols is None:
        return None
    match.update(symbols)
    del match["symbol"]
    equivalence = equivalence.format(**match)
    return equivalence.split("|")
   
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
    elif t_inst == "SO":
        return info["inst"][token_instruction["operation"]]
    return binary

def instruction_manager(instruction, line):
    info, t_inst = get_info(instruction, line)
    if info:
        if isinstance(info, list):
            token_instruction, i = special_instruction(instruction, info)
            info = info[i]
        else:
            re = regular_expression(info["inst"].keys(), info["re"])
            token_instruction = tokenize(instruction, re)
        binary = compile_instruction(token_instruction, info, t_inst, line)
        # print(token_instruction, binary)
        return binary

def clean_instructions(instructions: str):
    result = re.sub(r'#.*$', '', instructions, flags=re.MULTILINE)
    result = re.sub(r'\s*$', '', result, flags=re.MULTILINE)
    result = re.sub(r'^\s*', '', result, flags=re.MULTILINE)
    return result

def get_all_labels(instructions: list, i=0, instructionsp=[]):
    for instruction in instructions.copy():
        label = confirm_label(instruction)
        if label:
            LABELS[label] = i
            i -= 1
            instructions.remove(instruction)
        else:
            match, equivalence = is_pseudo(instruction)
            if isinstance(match, dict):
                inst = compile_pseudo(equivalence, match, i)
                if inst is None:
                    instructions.remove(instruction)
                    get_all_labels(instructions, i+1)
                    inst = compile_instruction(equivalence, match, i)
                instructionsp += inst
                if len(inst) > 1:
                    i += 1
            else:
                instructionsp.append(instruction)
        i += 1
    return instructionsp
    
def pseudoinstructions(instructions: list):
    i = 0
    instructionsp = []
    for instruction in instructions:
        match, equivalence = is_pseudo(instruction)
        if match:
            inst = compile_pseudo(equivalence, match, i)
            instructionsp += inst
            i += 2
        else:
            instructionsp.append(instruction)
            i += 1
    return instructionsp
            
def main(file):
    instructions_file = read_file(file)
    instructions_file = clean_instructions(instructions_file)
    instructions = sep_lines(instructions_file)
    # instructions = pseudoinstructions(instructions)
    instructions = get_all_labels(instructions)
    
    for line, instruction in enumerate(instructions, 0):
        binary = instruction_manager(instruction, line)
        if binary:
            BINARY_INSTRUCTIONS.append(binary)
    return BINARY_INSTRUCTIONS

def valid(binary_instructions: list[str]):
    for i, element in enumerate(binary_instructions):
        binary = element[0].replace("-", "")
        if len(binary) != 32:
            print(f"Instruccion invalida: {i}\nBinario: {element[0]} Instruccion: {element[1]} len:{len(element[0])}")

main("./test.S")

# expected = values_prepare()
expected = ['00000000001100010000000010110011', '01000000011000101000001000110011', '00000000100101000100001110110011', '00000000110001011110010100110011', '00000000111101110111011010110011', '00000100110000010000001011100111', '00000001001010001001100000110011', '00000001010110100101100110110011', '01000001100010111101101100110011', '00000001101111010010110010110011', '00000001111011101011111000110011', '00000000101000010000000010010011', '00000000010100100111000110010011', '00000000111100110110001010010011', '00000000011101000100001110010011', '00000000000001010000010010000011', '00000000010001100001010110000011', '00000000100001110010011010000011', '00000000110010000100011110000011', '00000001000010010101100010000011', '00000000000100010000000000100011', '00000000001100100001001000100011', '00000000010100110010010000100011', '11111110100000111000000011100011', '00000000101001001001101001100011', '00000010110001011100011001100011', '11111100111001101101101011100011', '00010011100010000000000110010111', '10001000000000011000000110010011', '00000001000001111110111001100011', '00000011001010001111100001100011', '00000010110000000000100111101111', '00000000000010101000101001100111', '00000001000000000000101100110111', '00000010000000000000101110010111', '00000000000000000000000001110011', '00010011100010000000000110010111', '10001000000000011000000110010011', '00000000000000000000000000010011', '00000000000000010000000010010011', '11111111111100010100000010010011', '01000000001000000000000010110011', '00000000000100010011000010010011', '00000000001000000011000010110011', '00000000000000010010000010110011', '00000000001000000010000010110011', '11111000000000001000001011100011', '11111000000000001001000011100011', '11110110000100000101111011100011', '11110110000000001101110011100011', '11110110000000001100101011100011', '11110110000100000100100011100011', '11110110000100010100011011100011', '11110110000100010101010011100011', '11110110000100010110001011100011', '11110110000100010111000011100011']

for value in BINARY_INSTRUCTIONS:
    if not value in expected:
        print(value)
# push_info("./bin.bin", BINARY_INSTRUCTIONS)
# print(BINARY_INSTRUCTIONS)
# print(BINARY_INSTRUCTIONS)
