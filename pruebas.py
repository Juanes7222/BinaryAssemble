import re

pattern = re.compile(r"\.*\b[01]+\b")

with open("./binarys.txt") as f:
    text = f.read()
    match = re.findall(pattern, text)
    print(match)