from Crypto.Cipher import AES
from Crypto.Hash import SHA256


with open("encrypted_flag.txt","r") as f:
    data = eval(f.readline())

iv,ciphertext,p = data['iv'],data['ciphertext'],int(data['p'])
ciphertext, iv = bytes.fromhex(ciphertext), bytes.fromhex(iv)

def read_matrix(file_name):
    data = open(file_name, 'r').read().strip()
    rows = [list(eval(row)) for row in data.splitlines()]
    return Matrix(GF(p), rows)
def decrypt(ciphertext,iv,key):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = cipher.decrypt(ciphertext)
    return plaintext

G = read_matrix("matrix.txt")
A = read_matrix("public_key.txt")

"""
the main idea of this challenge is to check the diagonalizability of the matrix G,
As G is diagonalizable , then G = P^(-1)* D* P, where D = diag(x1,x2,...,x31),
we can easily check that G^e = P^(-1)* D ^e* P,and we know that D^s = diag(x1^e,x2^e,...,x31^e),
and now we have a classical DLP,p is relatively small so the DLP is solvable.
"""

assert G.is_diagonalizable()==True
SpecG  = sorted(list(G.eigenvalues()))
#print(SpecG)# primerange
SpecA = sorted(list(A.eigenvalues()))
for i  in range(len(SpecA)):
  try:
        priv = discrete_log(Mod(SpecA[11-i],p),Mod(SpecG[0],p),p-1)

        key = SHA256.new(data=str(priv).encode()).digest()[:2**8]
        flag = decrypt(ciphertext, iv, key)
        if b'CyberErudites{' in flag:
            print(flag)
            break


  except:
         print("prb")











