from qiskit import QuantumCircuit, assemble, Aer
sim = Aer.get_backend('aer_simulator')


def get_state(x):
    l = [0]* 2**len(x)
    l[int(x,2)] = 1
    return  l

def str2bin(s):
    return ''.join(bin(ord(i))[2:].zfill(8) for i in s)

def bin2str(a):
    return ''.join(chr(int(a[i:i+8],2)) for i in range(0,len(a),8))

def encode_1(initial_state):
    qc = QuantumCircuit(1)
    qc.initialize(initial_state)
    qc.x(0)
    qc.save_statevector()
    qobj = assemble(qc)
    state = sim.run(qobj).result()
    return list(state.get_statevector().real.astype(int))

def encode_2(initial_state):
    qc = QuantumCircuit(2)
    qc.initialize(initial_state)
    qc.cx(0,1)
    qc.save_statevector()
    qobj = assemble(qc)
    state = sim.run(qobj).result()
    return list(state.get_statevector().real.astype(int))

def encode_3(initial_state):
    qc = QuantumCircuit(3)
    qc.initialize(initial_state)
    qc.ccx(0,1,2)
    qc.save_statevector()


    qobj = assemble(qc)
    state = sim.run(qobj).result()
    return list(state.get_statevector().real.astype(int))



def  encrypt_1(word):
    enc = ""
    for _ in range(len(word)):
        st = get_state(word[_])
        enc+= ''.join(str(x) for x in encode_1(st))
    return enc
def encrypt_2(word):
    enc = ""
    for _ in range(0,len(word),2):
        st = get_state(word[_:_+2])
        enc+= ''.join(str(x) for x in encode_2(st))
    return enc
def encrypt_3(word):
    enc = ""
    for _ in range(0,len(word),3):
        st = get_state(word[_:_+3])
        enc+= ''.join(str(x) for x in encode_3(st))
    return enc


with open("flag.txt","r") as f:
    flag = f.read()

flag = str2bin(flag)

enc_1 = encrypt_1(flag)

enc_2 = encrypt_2(enc_1)

enc_3 = encrypt_3(enc_2)

with open("enc.txt","w") as f:
    f.write(bin2str(enc_3))

