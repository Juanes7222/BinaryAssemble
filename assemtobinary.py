import json
import re

INSTRUCTIONS_FILE = "./instructions_info.json"

def get_instructions_info():
    with open(INSTRUCTIONS_FILE, "r") as f:
        info = json.loads(f)
    return info

INFO = get_instructions_info() 

def read_file(file):
    with open(file, "r", encoding="utf-8") as f:
        text_file = f.read()
    return text_file

def sep_lines(text: str):
    return text.split("\n")

def tokenize(expr, i_type):
    info = INFO[i_type]
    pattern = re.compile(info["stmt"].replace("expr", info["inst"]))
    match_instruction = pattern.match(expr)
    if match_instruction:
        ... 