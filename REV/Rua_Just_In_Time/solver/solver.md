# Rua Just In Time 문제 풀이

## 문제 분석

이 문제는 Lua JIT 컴파일러를 활용한 리버싱 문제입니다. 주어진 바이너리는 입력받은 플래그를 검증하는 프로그램입니다.

## 풀이 과정

1. **바이너리 분석**
   - 프로그램은 Lua JIT를 사용하여 플래그 검증 로직을 실행합니다
   - 입력된 문자열을 특정 알고리즘으로 변환한 후 하드코딩된 값과 비교합니다

2. **검증 로직 추출**
   - 프로그램 내부의 Lua 코드를 분석하여 플래그 검증 알고리즘을 파악합니다
   - XOR 연산과 특정 상수들을 사용하여 플래그를 인코딩합니다
   - 구조체 파악

3. **역연산 구현**
   - solver.py에서 검증 로직의 역연산을 구현합니다
   - 하드코딩된 결과값으로부터 원본 플래그를 복원합니다

## 플래그

실행 결과: 

```
star@Kind-Killerwhale:~/KCTF-jr-2025/REV/Rua_Just_In_Time/public$ ./Rua_Just_In_Time kctf-jr{2ba0fc74c0db3117617f5343f7269ce7612324b541c881f53ac2693812c1884b}
libunwind: __unw_add_dynamic_fde: bad fde: FDE is really a CIE
correct
```