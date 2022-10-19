import os
import time

t = os.system("chmod +x ")
print(f"[-] Finding Length")
times = {}
for i in range(15):
    times[i] = 0
for j in range(5):
    for i in range(15):
        cmd = 'echo "'+str(1)*i+'" | ./dark_dimention.exe > /dev/null 2>&1'
        # print(f"input: {str(1)*i}")
        start_time = time.time()
        t = os.system(cmd)
        xx = (time.time() - start_time)
        times[i] += xx
        # print(f"I= {i} --- {(time.time() - start_time)} seconds ---")
# print({k: v for k, v in sorted(times.items(), key=lambda item: item[1])})
length = max(times, key=times.get)
print(f"[+] Done {length}")
print(f"[-] Finding Code")
password = ""
for j in range(length):
    print(f"    [-] degit number: {j+1}")
    times = {}
    for i in range(10):
        cmd = 'echo "'+password+str(i)+(length - len(password)-1)*'1'+'" | ./dark_dimention.exe > /dev/null 2>&1'
        start_time = time.time()
        t = os.system(cmd)
        xx = (time.time() - start_time)
        times[i] = xx
    nbr = max(times, key=times.get)
    password += str(nbr)
    print(f"    [+] Done: {nbr}")
print(f"[+] Done {password}")