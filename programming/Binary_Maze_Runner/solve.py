#!/usr/bin/env python3
import socket
import re
import time
import threading


class BinaryMazeSolver:
    def __init__(self, host='localhost', port=9004):
        """Binary Maze 서버 클라이언트 초기화"""
        self.host = host
        self.port = port
        self.sock = None
        self.current_array = []  # 현재 배열 상태 추적
        self.array_lock = threading.Lock()  # 배열 수정 동기화
        self.modification_buffer = []  # 수정 메시지 버퍼

    def connect(self):
        """서버에 연결"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        print(f"Connected to Binary Maze Runner server at {self.host}:{self.port}")

    def receive_data(self, size=65536):
        """소켓에서 데이터 수신 - 큰 배열을 위해 버퍼 크기 증가"""
        return self.sock.recv(size).decode()

    def receive_until(self, delimiter, timeout=10):
        """특정 구분자를 찾을 때까지 데이터 수신"""
        buffer = ""
        start_time = time.time()

        while delimiter not in buffer and time.time() - start_time < timeout:
            try:
                new_data = self.sock.recv(4096).decode()
                if not new_data:
                    break
                buffer += new_data
            except socket.timeout:
                break

        return buffer

    def parse_array_from_data(self, data):
        """수신한 데이터에서 배열 추출 - 새로운 형식 처리"""
        # 새 형식: Array (size=N): [...]
        match = re.search(r'Array \(size=(\d+)\): \[(.*?)\]', data, re.DOTALL)
        if match:
            size = int(match.group(1))
            array_str = match.group(2).strip()

            # 큰 배열의 경우 발생할 수 있는 줄바꿈 처리
            array_str = array_str.replace('\n', ' ').replace('\r', '')

            if array_str:
                numbers = [n.strip() for n in array_str.split(',') if n.strip()]
                return [int(n) for n in numbers]

        # 이전 형식 대비: Array: [...]
        match = re.search(r'Array: \[(.*?)\]', data, re.DOTALL)
        if match:
            array_str = match.group(1).strip()
            array_str = array_str.replace('\n', ' ').replace('\r', '')
            numbers = [n.strip() for n in array_str.split(',') if n.strip()]
            return [int(n) for n in numbers]

        return None

    def apply_modification(self, mod_line):
        """수정 메시지를 파싱하여 현재 배열에 적용"""
        with self.array_lock:
            try:
                if 'INSERT' in mod_line:
                    # INSERT at index X value Y
                    match = re.search(r'INSERT at index (\d+) value (\d+)', mod_line)
                    if match:
                        index = int(match.group(1))
                        value = int(match.group(2))
                        if 0 <= index <= len(self.current_array):
                            self.current_array.insert(index, value)
                            print(f"[APPLIED] INSERT at {index} value {value}")

                elif 'REMOVE' in mod_line:
                    # REMOVE at index X (was Y)
                    match = re.search(r'REMOVE at index (\d+)', mod_line)
                    if match:
                        index = int(match.group(1))
                        if 0 <= index < len(self.current_array):
                            removed = self.current_array.pop(index)
                            print(f"[APPLIED] REMOVE at {index} (was {removed})")

                elif 'MODIFY' in mod_line:
                    # MODIFY at index X from Y to Z (now at index W)
                    match = re.search(r'MODIFY at index (\d+) from (\d+) to (\d+) \(now at index (\d+)\)', mod_line)
                    if match:
                        old_index = int(match.group(1))
                        old_value = int(match.group(2))
                        new_value = int(match.group(3))
                        new_index = int(match.group(4))

                        # 먼저 제거
                        if 0 <= old_index < len(self.current_array):
                            self.current_array.pop(old_index)

                        # 새 위치에 삽입
                        if 0 <= new_index <= len(self.current_array):
                            self.current_array.insert(new_index, new_value)
                            print(f"[APPLIED] MODIFY: {old_value} → {new_value} (index {old_index} → {new_index})")

            except Exception as e:
                print(f"[ERROR] Failed to apply modification: {e}")

    def binary_search(self, arr, target):
        """표준 이진 탐색 - 인덱스 반환 또는 -1"""
        left, right = 0, len(arr) - 1

        while left <= right:
            mid = (left + right) // 2
            if arr[mid] == target:
                return mid
            elif arr[mid] < target:
                left = mid + 1
            else:
                right = mid - 1

        return -1

    def binary_search_first(self, arr, target):
        """첫 번째 발생 위치 찾기 - 중복 값이 있을 때 가장 왼쪽 인덱스 반환"""
        left, right = 0, len(arr) - 1
        result = -1

        while left <= right:
            mid = (left + right) // 2
            if arr[mid] == target:
                result = mid
                right = mid - 1  # 더 왼쪽에 있는지 계속 탐색
            elif arr[mid] < target:
                left = mid + 1
            else:
                right = mid - 1

        return result

    def wait_for_pattern(self, buffer, pattern, timeout=10):
        """버퍼에 특정 패턴이 나타날 때까지 대기"""
        start_time = time.time()
        while pattern not in buffer and time.time() - start_time < timeout:
            try:
                new_data = self.receive_data()
                buffer += new_data

                # 배열 수정 메시지 처리
                if '🔄 ARRAY MODIFIED' in new_data:
                    modification_lines = [line for line in new_data.split('\n') if '🔄 ARRAY MODIFIED' in line]
                    for mod_line in modification_lines:
                        print(f"[MODIFICATION] {mod_line}")
                        self.modification_buffer.append(mod_line)
                        # Room 3에서만 실시간 적용
                        if self.current_room == 3:
                            self.apply_modification(mod_line)

            except socket.timeout:
                break
        return buffer

    def wait_for_array_complete(self, buffer, timeout=10):
        """버퍼에 완전한 배열이 들어올 때까지 대기"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            # 배열이 시작되었는지 확인
            if 'Array (size=' in buffer or 'Array:' in buffer:
                # 닫는 대괄호를 찾아 배열이 완전한지 확인
                array_start = buffer.find('Array')
                if array_start != -1:
                    bracket_count = 0
                    found_opening = False

                    for i in range(array_start, len(buffer)):
                        if buffer[i] == '[':
                            bracket_count += 1
                            found_opening = True
                        elif buffer[i] == ']':
                            bracket_count -= 1
                            if found_opening and bracket_count == 0:
                                # 완전한 배열을 찾음
                                return buffer

            # 더 많은 데이터 필요
            try:
                new_data = self.receive_data()
                if not new_data:
                    break
                buffer += new_data
            except socket.timeout:
                break

        return buffer

    def solve(self):
        """메인 문제 해결 로직"""
        try:
            self.connect()

            # 환영 메시지 읽기
            buffer = ""
            buffer = self.wait_for_pattern(buffer, "Complete 3 rooms to escape with the flag!")
            print("\n=== Game Started ===")

            # 각 방 처리
            for room in range(1, 4):
                self.current_room = room  # 현재 방 번호 저장
                self.modification_buffer = []  # 수정 버퍼 초기화

                print(f"\n{'=' * 50}")
                print(f"ROOM {room}")
                print('=' * 50)

                # 방 헤더 대기
                buffer = self.wait_for_pattern(buffer, f"--- Room {room} ---")

                # 방 헤더 이후 버퍼를 초기화하여 새로운 데이터만 처리
                room_start_pos = buffer.rfind(f"--- Room {room} ---")
                buffer = buffer[room_start_pos:]

                # 완전한 배열 대기
                buffer = self.wait_for_array_complete(buffer)

                # 버퍼에서 가장 최근 배열 찾기
                array_matches = list(re.finditer(r'Array \(size=\d+\): \[.*?\]', buffer, re.DOTALL))
                if not array_matches:
                    array_matches = list(re.finditer(r'Array: \[.*?\]', buffer, re.DOTALL))

                if array_matches:
                    # 가장 최근(마지막) 배열 매치 사용
                    last_match = array_matches[-1]
                    array_data = buffer[last_match.start():last_match.end()]
                    array = self.parse_array_from_data(array_data)
                else:
                    print("ERROR: Could not find array!")
                    print(f"Buffer content:\n{buffer[-1000:]}")
                    return

                if array is None:
                    print("ERROR: Could not parse array!")
                    return

                # 현재 배열 설정
                with self.array_lock:
                    self.current_array = array[:]

                print(f"Array loaded: {len(array)} elements")
                if len(array) <= 50:
                    print(f"Array: {array}")
                else:
                    print(f"First 10: {array[:10]}")
                    print(f"Last 10: {array[-10:]}")

                # 방 번호에 따른 쿼리 개수 결정 - Room 3는 50개!
                query_counts = {1: 3, 2: 4, 3: 100}
                num_queries = query_counts[room]
                print(f"Total queries for Room {room}: {num_queries}")

                # 쿼리 처리
                for q in range(num_queries):
                    # 쿼리 대기
                    buffer = self.wait_for_pattern(buffer, f"Query {q + 1}:", timeout=30)
                    buffer = self.wait_for_pattern(buffer, "Index: ", timeout=30)

                    # 버퍼에서 가장 최근 쿼리 찾기
                    query_pattern = rf'Query {q + 1}: (.+?)\n.*?Index:'
                    query_matches = list(re.finditer(query_pattern, buffer, re.DOTALL))

                    if query_matches:
                        # 가장 최근(마지막) 매치 사용
                        query_match = query_matches[-1]
                        query_text = query_match.group(1).strip()

                        # Room 3에서는 진행상황 표시
                        print(f"\n[{q + 1}/{num_queries}] Query: {query_text}")

                        # 타겟과 쿼리 타입 파싱
                        answer = None
                        target = None

                        # 현재 배열 상태 사용 (Room 3에서는 동적으로 변경됨)
                        with self.array_lock:
                            current_array_copy = self.current_array[:]

                        if "Find FIRST occurrence of" in query_text:
                            # 첫 번째 발생 위치 찾기
                            target_match = re.search(r'Find FIRST occurrence of (\d+)', query_text)
                            if target_match:
                                target = int(target_match.group(1))
                                answer = self.binary_search_first(current_array_copy, target)
                        else:
                            # 일반 이진 탐색
                            target_match = re.search(r'Find (\d+)', query_text)
                            if target_match:
                                target = int(target_match.group(1))
                                answer = self.binary_search(current_array_copy, target)

                        if answer is not None and target is not None:
                            print(f"Target: {target}, Answer: {answer}")

                            # 답변 전송
                            self.sock.send(f"{answer}\n".encode())

                            # 응답 읽기
                            response = self.receive_data()
                            buffer += response

                            # 수정 메시지 처리
                            if '🔄 ARRAY MODIFIED' in response:
                                modification_lines = [line for line in response.split('\n') if
                                                      '🔄 ARRAY MODIFIED' in line]
                                for mod_line in modification_lines:
                                    print(f"[MODIFICATION] {mod_line}")
                                    if room == 3:
                                        self.apply_modification(mod_line)

                            # 결과 라인 추출
                            response_lines = response.strip().split('\n')
                            if response_lines:
                                result_line = response_lines[0]
                                # 수정 메시지와 결과 메시지 구분 처리
                                for line in response_lines:
                                    if 'Correct!' in line or 'Wrong!' in line:
                                        result_line = line
                                        break

                                if room == 3:
                                    # Room 3에서는 간단히 표시
                                    if "Correct!" in result_line:
                                        print(f"✓ Correct!")
                                    else:
                                        print(f"✗ {result_line}")
                                else:
                                    print(f"Server: {result_line}")

                                if "Wrong!" in result_line:
                                    print("\n[FAILED] Incorrect answer!")
                                    # 디버그 정보 출력 (있는 경우)
                                    for line in response_lines[1:]:
                                        if '(Debug:' in line:
                                            print(line)
                                    return
                    else:
                        print(f"ERROR: Could not find Query {q + 1}")
                        return

                # 방 클리어 메시지 대기
                buffer = self.wait_for_pattern(buffer, f"Room {room} cleared!", timeout=30)
                print(f"\n✓ Room {room} cleared!")

            # 플래그 대기
            buffer = self.wait_for_pattern(buffer, "kctf-jr{", timeout=10)

            print(f"\n{'=' * 50}")
            print("SUCCESS!")
            print('=' * 50)

            # 플래그 추출
            flag_match = re.search(r'(kctf-jr\{[^}]+})', buffer)
            if flag_match:
                print(f"\n🎉 FLAG: {flag_match.group(1)} 🎉")
            else:
                # 플래그를 찾지 못한 경우 버퍼의 마지막 부분 출력
                print("Flag not found. Last buffer content:")
                print(buffer[-500:])

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.sock:
                self.sock.close()


if __name__ == "__main__":
    import sys

    # 명령줄 인자로 호스트와 포트 받기
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 9004

    solver = BinaryMazeSolver(host=host, port=port)
    solver.solve()