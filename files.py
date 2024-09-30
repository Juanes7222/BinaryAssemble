
def push_info(file: str, info: list):
    byte_data = bytearray()

    for binary_str in info:
        # Divide la cadena binaria en bloques de 8 bits
        for i in range(0, len(binary_str), 8):
            byte_chunk = binary_str[i:i+8]
            byte_data.append(int(byte_chunk, 2))

    
    with open(file, "wb") as f:
            f.write(byte_data)