from values import INSTRUCTIONS_FILE, BINARY_INSTRUCTIONS, LABELS
from functools import singledispatch
from utils import get_instructions_info, read_file, sep_lines, confirm_label, is_pseudo, cut_symbol
from compiler import r_instruction, i_instruction, b_instruction, u_instruction, s_instruction, j_instruction
from files import push_info_bin, push_info_hex, push_str_bin, push_str_bin_quartus, push_str_hex
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
    
def main(file):
    instructions_file = read_file(file)
    instructions_file = clean_instructions(instructions_file)
    instructions = sep_lines(instructions_file)
    instructions = get_all_labels(instructions)
    
    for line, instruction in enumerate(instructions, 0):
        binary = instruction_manager(instruction, line)
        if binary:
            BINARY_INSTRUCTIONS.append(binary)
    push_info_bin("./output/bin.bin", BINARY_INSTRUCTIONS)
    push_info_hex("./output/hex.hex", BINARY_INSTRUCTIONS)
    push_str_bin("./output/instructions.txt", BINARY_INSTRUCTIONS)
    push_str_bin_quartus("./output/instructions_quartus.txt", BINARY_INSTRUCTIONS)
    push_str_hex("./output/instructions_hex.hex", BINARY_INSTRUCTIONS)
    return BINARY_INSTRUCTIONS

def valid(binary_instructions: list[str]):
    for i, element in enumerate(binary_instructions):
        binary = element[0].replace("-", "")
        if len(binary) != 32:
            print(f"Instruccion invalida: {i}\nBinario: {element[0]} Instruccion: {element[1]} len:{len(element[0])}")

print(main("./instruction.S"))


