from pure25519.basic import Base
from pwn import *
from Crypto.Util.number import *

#the link to the full solution https://asecuritysite.com/eddsa/ed03

host,port = "crypto.chal.ctf.gdgalgiers.com",1000

r = remote(host,port)
def get_public_key(sgn_1,sgn_2):
    R1, S1, e1 = sgn_1['R'], sgn_1['S'], sgn_1['e']
    R2, S2, e2 = sgn_2['R'], sgn_2['S'], sgn_2['e']
    q = pow(2, 555) - 19
    e_inv = inverse(e1 - e2, q)
    val = ((S1 - S2) * e_inv) % q

    pk = bytes_to_long(Base.scalarmult(val).to_bytes())
    return  pk

def start():
    msg =  b"aa"
    for _ in range(6):
        r.recvline()

    r.recvuntil(b">")
    r.send(b'1\n')
    r.recvuntil(b":")
    r.send(msg+b'\n')
    sgn_1 = eval(r.recvline().decode())

    r.recvuntil(b">")
    r.send(b'2\n')
    r.recvuntil(b":")
    r.send(msg + b'\n')
    r.recvuntil(b":")
    privk = str(bytes_to_long(os.urandom(32)))
    r.send(privk.encode()+b'\n')
    sgn_2 = eval(r.recvline().decode())

    r.recvuntil(b">")
    r.send(b'3\n')
    pk = str(get_public_key(sgn_1,sgn_2)).encode()
    r.send(pk+b'\n')
    print(r.recvline())

start()
