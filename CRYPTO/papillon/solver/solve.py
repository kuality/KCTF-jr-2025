import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

with open("./flag.jpg.enc", "rb") as f:
    ciphertext = f.read()

for x in range(0x10):
    for y in range(0x10):
        for z in range(0x10):
            seed = (x << 8) | (y << 12) | (z << 28)
            random.seed(seed)
            key = bytes([random.randint(0, 255) for _ in range(16)])
            
            cipher = AES.new(key, AES.MODE_ECB)
            plaintext = cipher.decrypt(ciphertext)

            if b"JFIF" in plaintext:
                with open("./flag.jpg", "wb") as f:
                    f.write(unpad(plaintext, 16))
                    exit(0)