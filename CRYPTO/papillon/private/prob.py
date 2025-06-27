import random
from random import _urandom
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

rand_bytes = int.from_bytes(_urandom(4), byteorder="little")
seed = rand_bytes & 0xF000FF00
random.seed(seed)
key = bytes([random.randint(0, 255) for _ in range(16)])
with open("./flag.jpg", "rb") as f:
    plaintext = f.read()
cipher = AES.new(key, AES.MODE_ECB)
ciphertext = cipher.encrypt(pad(plaintext, 16))

with open("./flag.jpg.enc", "wb") as f:
    f.write(ciphertext)