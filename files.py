
from intelhex import IntelHex

def push_info_bin(file: str, info: list):
    byte_data = bytearray()

    for binary_str in info:
        # Divide la cadena binaria en bloques de 8 bits
        for i in range(0, len(binary_str), 8):
            byte_chunk = binary_str[i:i+8]
            binary = int(byte_chunk, 2)
            byte_data.append(binary)

    
    with open(file, "wb") as f:
            f.write(byte_data)
            
def push_info_hex(file: str, info: list):
    ih = IntelHex()
    address = 0
    
    for binary_str in info:
        # Divide la cadena binaria en bloques de 8 bits
        for i in range(0, len(binary_str), 8):
            byte_chunk = binary_str[i:i+8]
            binary = int(byte_chunk, 2)
            ih[address] = binary
            address += 1
    ih.write_hex_file(file)
    