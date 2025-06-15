#!/usr/bin/env python3
import hashlib

def decrypt_char(target_val, i):
    for c in range(32, 127):
        if i % 3 == 0:
            val = (ord(chr(c)) ^ 0x42) + 3
        elif i % 3 == 1:
            val = (ord(chr(c)) ^ 0x37) - 5
        else:
            val = (ord(chr(c)) ^ 0x55) + 7
        
        if (val & 0xFF) == target_val:
            return chr(c)
    return None

def solve():
    target = [0x1d, 0x09, 0x3f, 0x0c, 0xff, 0x2c, 0x16, 0xfb, 0x2a, 0x0f, 
              0x00, 0x2d, 0x07, 0x0a, 0x46, 0x11, 0xfe, 0x36, 0x66]
    
    answer = ""
    for i in range(19):
        char = decrypt_char(target[i], i)
        if char:
            answer += char
        else:
            return None
    
    return answer

if __name__ == "__main__":
    print("Solving rev_basic_1...")
    answer = solve()
    
    if answer:
        print(f"Answer: {answer}")
        flag_hash = hashlib.sha256(answer.encode()).hexdigest()
        print(f"Flag: kctf-jr{{{flag_hash}}}")
    else:
        print("No solution found")