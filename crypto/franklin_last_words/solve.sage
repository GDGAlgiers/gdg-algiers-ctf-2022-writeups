from string import printable
from message import ct, N, e

C1 = ct[1]
C2 = ct[0]

b = pow(ord('C'), e, N)

Z = Zmod(N)
P.<x> = PolynomialRing(Z)
def pgcd(g1,g2):
    return g1.monic() if not g2 else pgcd(g2, g1%g2)
g1 = (x + b)^e - C1
g2 = x^e - C2
M2 = -pgcd(g1, g2).coefficients()[0]

r = M2 >> 24
# yes we could just use M2 instead of computing r << 24, but this is easier to understand
mapping = { pow(pow(ord(c), 3, N) + (r << 24), e, N):c for c in printable }
flag = ''
for c in ct[1:]:
    flag += mapping[c]
print(flag)
