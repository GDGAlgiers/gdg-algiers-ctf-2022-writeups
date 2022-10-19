from values import *
import string

flag = ''
for c in ct:
    for char in string.printable:
        if pow(ord(char),e, N) == c :
            flag = flag +char
    print(flag)
