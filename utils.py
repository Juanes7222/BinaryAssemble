from bitstring import Bits, BitArray
from values import EQUIVALENCES, LABELS, PSEUDOINSTRUCTIONS_FILE
import json
import re


def read_file(file):
    with open(file, "r", encoding="utf-8") as f:
        text_file = f.read()
    return text_file

def get_instructions_info(file):
    with open(file, "r") as f:
        info = json.load(f)
    return info

PSEUDOINSTRUCTIONS: dict = get_instructions_info(PSEUDOINSTRUCTIONS_FILE)

def sep_lines(text: str):
    list_text = text.split("\n")
    return list(filter(None, list_text))

def number_to_binary(number: int | str, length=4, signed=True):
    if isinstance(number, str):
        if "0x" in number:
            number = int(number, 16)
    binary = int(number).to_bytes(length=5, signed=signed)
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
        
def is_pseudo(instruction: str):
    for pattern, equivalence in PSEUDOINSTRUCTIONS.items():
        match = re.match(fr"{pattern}", instruction)
        if match:
            dict_ = match.groupdict()
            return match.groupdict(), equivalence
    return False, False

def cut_symbol(symbol: str, line=None):
    try:
        symbol = distance_label(symbol,line)
    except ValueError:
        if confirm_label(symbol):
            return None

    symbol = BitArray(uint=int(symbol), length=32)
    symbol1 = symbol << 12    
    new_symbol = {
        "symbol1": bin_to_decimal(symbol1.bin[:20]),
        "symbol2": bin_to_decimal(symbol.bin[-12:]),
    }
    return new_symbol

def values_prepare():
    with open("./binary_values.txt", "r") as f:
        txt = f.read()
    list_ = txt.strip().split("\n")
    return list_