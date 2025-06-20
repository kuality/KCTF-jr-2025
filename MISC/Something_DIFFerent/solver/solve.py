import os

base = os.path.dirname(__file__)
file1_path = os.path.join(base, "../public/First.txt")
file2_path = os.path.join(base, "../public/Second.txt")

with open(file1_path, "rb") as f1, open(file2_path, "rb") as f2:
    b1 = f1.read()
    b2 = f2.read()

tmp = ""

for i in range(len(b1)):
    if b1[i] != b2[i]:
        tmp += chr(b2[i])

flag = ""

for i in range(len(tmp) - 1, -1, -1):
    flag += tmp[i]

print(flag)
