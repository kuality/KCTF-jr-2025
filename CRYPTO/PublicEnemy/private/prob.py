import random
from Crypto.Util.number import isPrime, bytes_to_long

with open("flag", "rb") as f:
    FLAG = f.read()

def gen_param():
    t = random.getrandbits(1024)
    p, q = t, t
    while not isPrime(p):
        p = t + random.randint(2**20, 2**30)
    while not isPrime(q):    
        q = t + random.randint(2**20, 2**30)
    N = p * q
    return N, p, q

e = 0x10001
N, p, q = gen_param()

c = pow(bytes_to_long(FLAG), e, N)

print(f"N = {N}")
print(f"e = {e}")
print(f"c = {c}")