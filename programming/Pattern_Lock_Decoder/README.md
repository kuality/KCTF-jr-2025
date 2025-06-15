# Pattern Lock Decoder - Speed Challenge

## 문제 설명

금고는 Longest Common Subsequence (LCS) 알고리즘을 기반으로 한 DNA 패턴 잠금장치를 사용합니다! 금고를 열려면 각 보안 레벨에서 두 DNA 시퀀스 간의 LCS 길이를 빠르게 계산해야 합니다.

이것은 속도 도전 과제로, 각 레벨마다 점점 짧아지는 엄격한 시간 제한이 있습니다. DNA 시퀀스 길이가 증가하는 4개의 패턴 잠금장치를 시간과의 경쟁 속에서 해결해야 합니다. 가장 빠른 해결자만이 flag를 획득할 수 있습니다!

## 입력 형식

각 레벨에서 다음을 받게 됩니다:
1. A, C, G, T 염기만 포함하는 두 개의 DNA 시퀀스
2. LCS 길이를 묻는 프롬프트

시퀀스는 다음 형식으로 제공됩니다:
```
DNA Sequence 1: ACGTACGT...
DNA Sequence 2: CGTATGCA...
LCS Length: 
```

응답은 두 시퀀스 간의 longest common subsequence 길이를 나타내는 단일 정수여야 합니다.

## 출력 형식

- 쿼리당 LCS 길이를 나타내는 단일 정수
- 응답은 문자열 다음에 newline character를 포함하여 전송해야 함

## 제약 사항

### Level 1
- 시퀀스 길이: 8-12 문자
- 시간 제한: 30초
- DNA 염기: A, C, G, T만

### Level 2
- 시퀀스 길이: 15-25 문자
- 시간 제한: 20초
- DNA 염기: A, C, G, T만

### Level 3
- 시퀀스 길이: 30-40 문자
- 시간 제한: 15초
- DNA 염기: A, C, G, T만

### Level 4
- 시퀀스 길이: 50-70 문자
- 시간 제한: 10초
- DNA 염기: A, C, G, T만

### 일반 제약 사항
- 최대 동시 연결 수: 100
- 모든 시퀀스는 유효한 DNA 염기(A, C, G, T)만 포함
- 시간 제한은 엄격히 적용됨 - timeout 후 응답이 없으면 실패
- flag를 얻으려면 4개 레벨을 모두 연속적으로 완료해야 함

## 예제

### 예제 1: 기본 LCS 계산
```
DNA Sequence 1: ACGTACGT
DNA Sequence 2: CGTATGCA
LCS Length: 5

✅ Lock opened in 0.8 seconds! LCS length is 5
```

LCS는 "CGTAC"이며 길이는 5입니다.

### 예제 2: 공통 부분수열이 없는 경우
```
DNA Sequence 1: AAAA
DNA Sequence 2: CCCC
LCS Length: 0

✅ Lock opened in 0.2 seconds! LCS length is 0
```

### 예제 3: 시간 초과
```
DNA Sequence 1: ACGTACGTACGTACGT
DNA Sequence 2: GTCAGTCAGTCAGTCA
LCS Length: [20초 내 응답 없음]

❌ TIME'S UP! No answer received within 20 seconds!
```

### 예제 4: 빠른 해결자 보너스
```
DNA Sequence 1: ACGTGCTA
DNA Sequence 2: CGTACGTA
LCS Length: 6

✅ Lock opened in 1.2 seconds! LCS length is 6
🌟 AMAZING SPEED! You used only 15% of the time!
```

## 접근 방법/힌트

1. **Dynamic Programming**: 시간 복잡도 O(m×n)인 클래식 LCS 동적 프로그래밍 알고리즘을 사용하세요. 여기서 m과 n은 시퀀스의 길이입니다.

2. **공간 최적화**: 큰 시퀀스의 경우, O(m×n) 대신 O(min(m,n)) 공간만 사용하는 공간 최적화 DP를 고려하세요.

3. **구현 속도**: 
   - 연결하기 전에 LCS 알고리즘을 미리 구현하고 테스트하세요
   - 효율적인 자료구조를 사용하고 불필요한 연산을 피하세요
   - 더 빠른 I/O 방법 사용을 고려하세요

4. **시간 관리**:
   - 타이머는 네트워크 지연시간을 포함하므로 연결 오버헤드를 최소화하세요
   - 시퀀스를 빠르게 파싱하고 처리하세요
   - 계산 직후 즉시 답변을 전송하세요

5. **알고리즘 리마인더**: 두 시퀀스 간의 LCS는 두 원본 시퀀스 모두에서 부분수열로 나타나는 가장 긴 시퀀스입니다 (반드시 연속적일 필요는 없음).

## 태그/카테고리

- **Algorithms**: Dynamic Programming, Longest Common Subsequence
- **Data Structures**: 2D Arrays/Matrix, String Processing
- **Concepts**: Sequence Alignment, Bioinformatics
- **Difficulty**: Medium
- **Skills**: Algorithm Implementation, Speed Optimization, Network Programming