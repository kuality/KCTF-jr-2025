import os

base = os.path.dirname(__file__)
file2_path = os.path.join(base, "../public/file2.txt")
file3_path = os.path.join(base, "../public/file3.txt")

with open(file2_path, "rb") as f1, open(file3_path, "rb") as f2:
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
