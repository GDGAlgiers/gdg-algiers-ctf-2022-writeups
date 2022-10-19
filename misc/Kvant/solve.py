from qiskit import QuantumCircuit, assemble, Aer
import math
sim = Aer.get_backend('aer_simulator')


def str2bin(s):
    return ''.join(bin(ord(i))[2:].zfill(8) for i in s)

def bin2str(a):
    return ''.join(chr(int(a[i:i+8],2)) for i in range(0,len(a),8))

def decode_1(initial_state):
    qc = QuantumCircuit(1)
    qc.initialize(initial_state)
    qc.x(0)
    qc.save_statevector()
    qobj = assemble(qc)
    state = sim.run(qobj).result()
    l = list(state.get_statevector().real.astype(int))
    return ''.join(str(x) for x in l)

def decode_2(initial_state):
    qc = QuantumCircuit(2)
    qc.initialize(initial_state)
    qc.cx(0,1)
    qc.save_statevector()
    qobj = assemble(qc)
    state = sim.run(qobj).result()
    l = list(state.get_statevector().real.astype(int))
    return ''.join(str(x) for x in l)

def decode_3(initial_state):
    qc = QuantumCircuit(3)
    qc.initialize(initial_state)
    qc.ccx(0,1,2)
    qc.save_statevector()


    qobj = assemble(qc)
    state = sim.run(qobj).result()
    l = list(state.get_statevector().real.astype(int))
    return ''.join(str(x) for x in l)




def get_ket(inp):
    i = list(inp).index('1')
    l = len(inp)
    return bin(i)[2:].zfill(int(math.log2(l)))

def decrypt_1(enc_1):
    dec_bin = ''
    for i in range(0, len(enc_1), 2):
        state = [int(x) for x in enc_1[i:i+2]]
        dec_bin += get_ket(decode_1(state))
    return dec_bin

def decrypt_2(enc_2):
    enc_1 = ''
    for i in range(0, len(enc_2), 4):
        state = [int(x) for x in enc_2[i:i+4]]

        enc_1 +=  get_ket(decode_2(state))
    return enc_1

def decrypt_3(enc_3):
    enc_2 = ''
    for i in range(0, len(enc_3), 8):
        state = [int(x) for x in enc_3[i:i+8]]
        enc_2 += get_ket(decode_3(state))

    return enc_2

with open("enc.txt","rb") as f:
    enc_3 = str2bin(f.read().decode())


enc_2 = decrypt_3(enc_3)
print(enc_2)
enc_1 = decrypt_2(enc_2)
flag = decrypt_1(enc_1)
print(bin2str(flag))
