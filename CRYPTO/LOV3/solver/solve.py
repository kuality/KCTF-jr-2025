from math import gcd
from functools import reduce
from pwn import *

io = remote("localhost", 10403)

def egcd(a, b):
    if a == 0:
        return b, 0, 1
    else:
        g, x, y = egcd(b % a, a)
        return g, y - (b // a) * x, x

class PRNG:
    def __init__(self, M, A, C, state):
        self.M = M
        self.A = A
        self.C = C
    
        self.state = state

    def next(self):
        self.state = (self.A * self.state + self.C) % self.M
        return self.state

def modinv(b, n):
    g, x, _ = egcd(b, n)
    if g == 1:
        return x % n


def crack_unknown_increment(states, modulus, multiplier):
    increment = (states[1] - states[0] * multiplier) % modulus
    return increment


def crack_unknown_multiplier(states, modulus):
    multiplier = (states[2] - states[1]) * modinv(states[1] - states[0], modulus) % modulus
    return multiplier


def crack_unknown_modulus(states):
    diffs = [s1 - s0 for s0, s1 in zip(states, states[1:])]
    zeroes = [t2 * t0 - t1 * t1 for t0, t1, t2 in zip(diffs, diffs[1:], diffs[2:])]
    modulus = abs(reduce(gcd, zeroes))
    return modulus

hints = []
for _ in range(10):
    hints.append(int(io.recvline().split(b" : ")[1]))

modulus = crack_unknown_modulus(hints)
multiplier = crack_unknown_multiplier(hints, modulus)
increment = crack_unknown_increment(hints, modulus, multiplier)
io.success(f"modules : {modulus}")
io.success(f"multiplier : {multiplier}")
io.success(f"increment : {increment}")

prng = PRNG(modulus, multiplier, increment, hints[0])

for _ in range(9):
    prng.next()

for _ in range(100):
    io.sendlineafter(b"> ", str(prng.next()))

print(io.recvline().decode())