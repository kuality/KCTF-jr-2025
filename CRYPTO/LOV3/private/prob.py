#!/usr/bin/env python3
from Crypto.Util.number import *
import random

class PRNG:
    def __init__(self):
        self.M = getPrime(128)
        self.A = getPrime(128)
        self.C = getPrime(128)
    
        self.state = random.getrandbits(100)

    def next(self):
        self.state = (self.A * self.state + self.C) % self.M
        return self.state

class Game:
    def __init__(self):
        self.prng = PRNG()
        self.get_hint()

    def get_hint(self):
        for i in range(10):
            print(f"hint[{i}] : {self.prng.next()}")
    
    def start(self):
        for _ in range(100):
            answer = self.prng.next()
            num = int(input("answer > "))

            if num != answer:
                exit(0)

        with open("./flag", "rb") as f:
            print(f.read().decode())
    
if __name__ == "__main__":
    game = Game()
    game.start()