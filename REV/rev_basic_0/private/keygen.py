def stage1(x):
    x = x & 0xFFFFFFFF
    x = ((x & 0xFF00FF00) >> 8) | ((x & 0x00FF00FF) << 8)
    x ^= 0xDEADBEEF
    x = ((x << 13) | (x >> 19)) & 0xFFFFFFFF
    return x

def stage2(x):
    x = (x + 0x13371337) & 0xFFFFFFFF
    x = ((x & 0xF0F0F0F0) >> 4) | ((x & 0x0F0F0F0F) << 4)
    x ^= 0xCAFEBABE
    return x

def stage3(x):
    x = ((x >> 7) | (x << 25)) & 0xFFFFFFFF
    x = (x * 0x41414141) & 0xFFFFFFFF
    x ^= 0x5A5A5A5A
    return x

def generate_key():
    k1 = 0x41584557
    k2 = 0x48454746
    k3 = 0x41534458
    k1 = stage1(k1)
    k2 = stage2(k2)
    k3 = stage3(k3)
    return k1 ^ k2 ^ k3

def generate_verification_constants():
    seed = 0x12345678
    seed = stage1(seed)
    seed = stage2(seed)
    c1 = seed
    seed = stage3(seed)
    seed ^= generate_key()
    c2 = seed
    return c1, c2

def solve():
    c1, c2 = generate_verification_constants()
    key = generate_key()
    target = c1 ^ c2
    needed = target ^ key
    
    # reverse stage3
    x = needed
    x ^= 0x5A5A5A5A
    x = (x * 0xC4EC4EC1) & 0xFFFFFFFF  # inverse of 0x41414141
    x = ((x << 7) | (x >> 25)) & 0xFFFFFFFF
    
    # reverse stage2
    x ^= 0xCAFEBABE
    x = ((x & 0xF0F0F0F0) >> 4) | ((x & 0x0F0F0F0F) << 4)
    x = (x - 0x13371337) & 0xFFFFFFFF
    
    # reverse stage1
    x = ((x >> 13) | (x << 19)) & 0xFFFFFFFF
    x ^= 0xDEADBEEF
    x = ((x & 0xFF00FF00) >> 8) | ((x & 0x00FF00FF) << 8)
    
    return x

if __name__ == "__main__":
    answer = solve()
    print(f"Answer: {answer}")
    
    import hashlib
    flag = hashlib.sha256(str(answer).encode()).hexdigest()
    print(f"Flag: kctf-jr{{{flag}}}")