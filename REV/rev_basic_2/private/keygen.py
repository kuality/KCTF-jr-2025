import hashlib

def transform_char(c, i):
    val = ord(c)
    val = (val * 7 + 13) ^ (i * 3 + 5)
    val = (val << 1) | (val >> 7)
    val = val & 0xFF
    return val

def reverse_transform(target_val, i):
    for c in range(32, 127):
        if transform_char(chr(c), i) == target_val:
            return chr(c)
    return None

if __name__ == "__main__":
    target = [0x9c, 0xb5, 0x9e, 0xfa, 0x76, 0x4e, 0xca, 0xd7, 
              0x26, 0xfd, 0x8e, 0x56, 0xb6, 0xbe, 0x0e, 0x8d]
    
    answer = ""
    for i in range(16):
        char = reverse_transform(target[i], i)
        if char:
            answer += char
        else:
            print(f"Could not reverse transform for position {i}")
            break
    
    if len(answer) == 16:
        print(f"Answer: {answer}")
        flag_hash = hashlib.sha256(answer.encode()).hexdigest()
        print(f"Flag: kctf-jr{{{flag_hash}}}")
        
        # 검증
        transformed = [transform_char(answer[i], i) for i in range(16)]
        print(f"Verification: {transformed == target}")
    else:
        print("Failed to find complete answer")