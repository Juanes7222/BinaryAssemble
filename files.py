
def push_info(file: str, info: list):
    with open(file, "w+") as f:
        for bin in info:
            f.write(bin + "\n")