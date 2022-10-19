

# This file was *autogenerated* from the file solve.sage
from sage.all_cmdline import *   # import sage library

_sage_const_1 = Integer(1); _sage_const_0 = Integer(0); _sage_const_24 = Integer(24); _sage_const_3 = Integer(3)
from string import printable
from message import ct, N, e

C1 = ct[_sage_const_1 ]
C2 = ct[_sage_const_0 ]

b = pow(ord('C'), e, N)

Z = Zmod(N)
P = PolynomialRing(Z, names=('x',)); (x,) = P._first_ngens(1)
def pgcd(g1,g2):
    return g1.monic() if not g2 else pgcd(g2, g1%g2)
g1 = (x + b)**e - C1
g2 = x**e - C2
M2 = -pgcd(g1, g2).coefficients()[_sage_const_0 ]

r = M2 >> _sage_const_24 
# yes we could just use M2 instead of computing r << 24, but this is easier to understand
mapping = { pow(pow(ord(c), _sage_const_3 , N) + (r << _sage_const_24 ), e, N):c for c in printable }
flag = ''
for c in ct[_sage_const_1 :]:
    flag += mapping[c]
print(flag)

