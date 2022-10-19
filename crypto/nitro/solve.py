from collections import deque
from pwn import *
import string
from sage.all import *
valide_chars= string.ascii_letters+"{_}0123456789"

N,p,q,d = 8,2,29,2
RR = ZZ['x']
Cyc = RR([-1] + [0] * (N - 1) + [1])  # x^N-1
R = RR.quotient(Cyc)
Rq = RR.change_ring(Integers(q)).quotient(Cyc)
Rp = RR.change_ring(Integers(p)).quotient(Cyc)


def bin2str(a):
    return ''.join(chr(int(a[i:i+8],2)) for i in range(0,len(a),8))


def rotate(f_x: list, n):
    f_x = deque(f_x)
    f_x.rotate(-n)
    return list(f_x)


def getMode(l: list):
    return max(set(l), key=l.count)


def LLL_attack(h):
    l = len(h)
    A, I = matrix.circulant(h), matrix.identity(l)
    H = block_matrix(ZZ, [[I, A], [0 * I, q * I]])
    H = matrix(ZZ, H)
    H_red = H.LLL()
    return H_red




def decrypt(e: list, f_x: list):
    f_x = R(f_x)
    Fp_x = Rp(lift(1 / Rp(f_x)))
    e_x = Rq(e)
    a_x = Rq(f_x * e_x)
    a_x = ZZ['x']([coeff.lift_centered() for coeff in a_x.lift()])
    b_x = Rp(Fp_x * R(a_x))
    b_x = ''.join(str(x) for x in b_x)

    return bin2str(b_x)





def getByte(e,h):
    H_red = LLL_attack(h)
    flag = []
    for i in range(2 * N):
        for j in range(N):

            f_x = rotate(list(H_red[i])[:N], j)
            try:
                byte = decrypt(e, f_x)
                if byte in valide_chars:
                       flag.append(byte)
                else:
                     flag.append("*")
            except:
                continue
    return  getMode(flag)


def getFlag():
    flag = ''

    for j in range(11):
        r.recvline()

    for i in range(32):
        byte = []
        for _ in range(10):

            r.recvline()
            r.sendline(b"a")
            r.send(f"{i}".encode()+b'\n')
            e = eval(r.recvline().decode().split(": ")[1])
            h = eval(r.recvline().decode())
            byte.append(getByte(e,h))
        flag+=getMode(byte)
        print(flag)

host,port = "crypto.chal.ctf.gdgalgiers.com", 1001
r = remote(host,port)
getFlag()
"""
CyberErudites{_NTRU_LLL_4tt4ck_}
"""

