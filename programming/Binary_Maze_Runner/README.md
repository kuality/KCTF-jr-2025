# Binary Maze Runner

## 문제 설명

이진 탐색을 사용하여 보안 코드를 찾아 디지털 미로를 탐험하세요! 점점 어려워지는 세 개의 방을 통과해야 하며, 각 방에는 특정 목표 값을 찾아야 하는 정렬된 배열이 있습니다. 특별한 점은? 배열이 실시간으로 수정되어 탐색에 추가적인 복잡성을 더한다는 것입니다.

도전 과제를 완료하려면 세 방 각각에서 모든 쿼리에 성공적으로 답해야 합니다. 이진 탐색 알고리즘을 효율적으로 사용하여 요청된 값을 찾거나 배열에 없다는 것을 판단하세요.

## 입력 형식

각 쿼리에 대해 서버는 다음을 제공합니다:
1. 정렬된 정수 배열 (각 방 시작 시 표시됨)
2. 두 가지 형식 중 하나의 쿼리:
   - `Query N: Find X` - 값 X의 아무 위치나 찾기
   - `Query N: Find FIRST occurrence of X` - 값 X의 가장 왼쪽/첫 번째 위치 찾기

응답은 다음과 같아야 합니다:
- 목표 값의 0-based index
- 목표 값이 배열에 없으면 `-1`

## 출력 형식

- 각 쿼리마다: 인덱스(0-based)를 나타내는 단일 정수 또는 -1
- 응답은 문자열 다음에 newline character를 포함하여 전송해야 함

## 제약 사항

### Room 1
- 배열 크기: 10-100개 요소
- 값 범위: 1-1,000
- 쿼리 수: 3개
- 수정 간격: 3초
- 배열에 중복 없음

### Room 2
- 배열 크기: 100-1,000개 요소
- 값 범위: 1-10,000
- 쿼리 수: 4개
- 수정 간격: 1초
- 배열에 중복 없음

### Room 3
- 배열 크기: 1,000-10,000개 요소
- 값 범위: 1-100,000
- 쿼리 수: 100개
- 수정 간격: 1초
- 배열에 중복 값이 있을 수 있음

### 일반 제약 사항
- 최대 입력 길이: 20자
- Connection timeout: 240초 (4분)
- 게임 중 배열이 INSERT, REMOVE, MODIFY 작업으로 수정됨
- 모든 배열은 수정 후에도 정렬 상태 유지

## 예제

### 예제 1: 기본 Binary Search
```
Array (size=10): [2, 5, 8, 12, 16, 23, 38, 45, 56, 67]

Query 1: Find 23
Index: 5

✅ Correct! Found at index 5
```

### 예제 2: 값이 없는 경우
```
Array (size=10): [2, 5, 8, 12, 16, 23, 38, 45, 56, 67]

Query 2: Find 20
Index: -1

✅ Correct! Not in array -1
```

### 예제 3: First Occurrence 찾기 (중복이 있는 경우)
```
Array (size=15): [1, 3, 5, 5, 5, 8, 10, 10, 12, 15, 18, 20, 20, 20, 25]

Query 1: Find FIRST occurrence of 5
Index: 2

✅ Correct! Found at index 2
```

### 예제 4: 배열 수정
```
🔄 ARRAY MODIFIED: INSERT at index 3 value 15
(인덱스 3에 값 15가 삽입되어 이후 요소들이 shift됨)

🔄 ARRAY MODIFIED: REMOVE at index 7 (was 45)
(인덱스 7에 있던 값 45가 제거됨)

🔄 ARRAY MODIFIED: MODIFY at index 2 from 8 to 30 (now at index 5)
(인덱스 2의 값이 8에서 30으로 변경되었고, 정렬로 인해 인덱스 5로 이동함)
```

## 접근 방법/힌트

1. **Binary Search 구현**: 표준 binary search와 첫 번째 occurrence를 찾는 변형 버전을 모두 구현하세요 (중복 처리용).

2. **실시간 수정 처리**: 특히 Room 3에서는 배열이 자주 수정됩니다. 다음을 고려하세요:
   - 수정사항 발생 시 tracking
   - 로컬 배열 복사본에 수정사항 적용
   - 각 쿼리마다 가장 최신 배열 상태 사용

3. **효율성이 중요**: Room 3은 최대 10,000개 요소의 배열에서 100개의 쿼리를 처리해야 하므로, 효율적인 O(log n) binary search가 필수입니다.

4. **Edge Cases**: 
   - 빈 결과 (target not found)
   - 중복 값 ("first occurrence" 쿼리의 경우)
   - 배열 범위를 벗어난 값

5. **네트워크 통신**: 적절한 socket handling과 data parsing을 보장하세요. 특히 여러 receive buffer에 걸쳐 있을 수 있는 큰 배열의 경우 주의가 필요합니다.

## 태그/카테고리

- **Algorithms**: Binary Search, Search Algorithms
- **Data Structures**: Sorted Arrays
- **Concepts**: Real-time Data Modification, Network Programming
- **Difficulty**: Medium
- **Skills**: Algorithm Implementation, Socket Programming, Concurrent Data Handling