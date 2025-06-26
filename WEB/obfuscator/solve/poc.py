data = '286c346531376d3330336430376460306733676433663167346d346c306c3334342e271f0a1301161e'

# 1. 2글자씩 분리
pairs = [data[i:i+2] for i in range(0, len(data), 2)]
# 2. 리스트를 뒤집기
pairs.reverse()
# 3. 각 바이트를 0x55와 XOR 후 문자로 변환
flag = ''.join(chr(int(byte, 16) ^ 0x55) for byte in pairs)

print(flag)