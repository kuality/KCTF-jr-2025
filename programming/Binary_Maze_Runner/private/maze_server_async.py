#!/usr/bin/env python3
import asyncio
import random
import logging
from typing import List, Tuple, Optional
from enum import Enum

# 로깅 설정
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class QueryType(Enum):
    """쿼리 타입 열거형"""
    FIND = 'find'
    FIND_FIRST = 'first'


class RoomConfig:
    """각 방 레벨의 설정"""

    def __init__(self, size_range: Tuple[int, int], value_range: Tuple[int, int],
                 queries: int, modification_interval: float):
        self.size_range = size_range
        self.value_range = value_range
        self.queries = queries
        self.modification_interval = modification_interval


class ProblemServer:
    FLAG = "KCTF_Jr{binary_search_speedrunner_2025}"

    # 상수
    MAX_INPUT_LENGTH = 20
    MIN_ARRAY_SIZE = 10
    MAX_ARRAY_VALUE = 2000
    CONNECTION_TIMEOUT = 240  # 4분
    MAX_CONNECTIONS = 50

    # 방 설정
    ROOM_CONFIGS = {
        1: RoomConfig((10, 100), (1, 1000), 3, 3.0),
        2: RoomConfig((100, 1000), (1, 10000), 4, 3.0),
        3: RoomConfig((1000, 10000), (1, 100000), 100, 3.0)
    }

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.active_connections = 0
        self.total_connections = 0
        self.connection_semaphore = asyncio.Semaphore(self.MAX_CONNECTIONS)

    async def run(self):
        server = await asyncio.start_server(self.on_connect, host=self.host, port=self.port)
        logging.info(f"Binary Maze Runner server started on {self.host}:{self.port}")
        logging.info(f"Maximum concurrent connections: {self.MAX_CONNECTIONS}")
        await server.wait_closed()

    async def on_connect(self, reader, writer):
        peername = writer.get_extra_info('peername')

        async with self.connection_semaphore:
            self.active_connections += 1
            self.total_connections += 1
            client_id = self.total_connections

            logging.info(f"Client {client_id} connected: {peername}")
            logging.info(f"Active connections: {self.active_connections}")

            def cleanup(fu):
                try:
                    fu.result()
                except Exception as e:
                    logging.error(f"Exception in client {client_id} connection: {e}")

                self.active_connections -= 1
                logging.info(f"Client {client_id} disconnected. Active connections: {self.active_connections}")

            task = asyncio.create_task(self.handle_client(reader, writer, client_id))
            task.add_done_callback(cleanup)

    async def handle_client(self, reader, writer, client_id):
        try:
            await asyncio.wait_for(self.handle_problem(reader, writer, client_id),
                                   timeout=self.CONNECTION_TIMEOUT)
        except asyncio.TimeoutError:
            logging.warning(f"Client {client_id} connection timed out.")
            await self.safe_write(writer, "❌ Connection timeout!\n".encode(), client_id)
            writer.close()
            await writer.wait_closed()

    async def handle_problem(self, reader, writer, client_id):
        # 환영 메시지
        welcome = """
=== Binary Maze Runner ===
Navigate through the digital maze by finding security codes!
Each room contains a sorted array - use binary search wisely.

Answer with the index of the target (0-based), or -1 if not found.
For 'first occurrence' queries, find the leftmost index.

  WARNING: Arrays are being modified in real-time!

Complete 3 rooms to escape with the flag!
"""
        if not await self.safe_write(writer, welcome.encode(), client_id):
            logging.info(f"Client {client_id} failed to send welcome message")
            return

        await asyncio.sleep(0.1)

        # 3개의 방 모두 처리
        for room in range(1, 4):
            success = await self.handle_room(reader, writer, room, client_id)
            if not success:
                logging.info(f"Client {client_id} failed at room {room}")
                writer.close()
                await writer.wait_closed()
                return

        # 모든 방 클리어 - 플래그 전송
        logging.info(f"Client {client_id} all rooms completed! Sending flag: {self.FLAG[:15]}...{self.FLAG[-5:]}")
        flag_message = f"\n🎉 MAZE COMPLETED! Here's your flag: {self.FLAG}\n"
        await self.safe_write(writer, flag_message.encode(), client_id)
        await self.safe_write(writer, b"Congratulations, Binary Search Master!\n", client_id)
        logging.info(f"Client {client_id} flag delivered successfully!")

        writer.close()
        await writer.wait_closed()

    async def handle_room(self, reader, writer, room: int, client_id: int) -> bool:
        """단일 방 챌린지 처리"""
        logging.info(f"Client {client_id} starting Room {room}")

        if not await self.safe_write(writer, f"\n--- Room {room} ---\n".encode(), client_id):
            return False

        # 방 데이터 생성
        arr, queries = self.generate_room(room)
        current_array = arr[:]
        array_lock = asyncio.Lock()

        # 배열 전송
        if not await self.safe_write(writer, f"Array (size={len(arr)}): {arr}\n\n".encode(), client_id):
            return False

        # 수정 작업 시작
        config = self.ROOM_CONFIGS[room]
        stop_event = asyncio.Event()
        modification_task = asyncio.create_task(
            self.modification_task(writer, current_array, array_lock,
                                   config.modification_interval, client_id, stop_event)
        )

        try:
            # 각 쿼리 처리
            for i, (target, query_type) in enumerate(queries):
                if query_type == QueryType.FIND_FIRST:
                    query_msg = f"Query {i + 1}: Find FIRST occurrence of {target}\nIndex: "
                else:
                    query_msg = f"Query {i + 1}: Find {target}\nIndex: "

                if not await self.safe_write(writer, query_msg.encode(), client_id):
                    return False

                try:
                    # 답변 읽기
                    response_data = await self.readLine(reader)
                    response = response_data.strip()

                    # 현재 배열 상태 확인
                    async with array_lock:
                        array_size = len(current_array)
                        current_array_copy = current_array[:]

                    # 입력 검증
                    user_answer = self.validate_input(response, array_size)

                    # 예상 답변 계산
                    if query_type == QueryType.FIND_FIRST:
                        expected_original = self.binary_search_first(arr, target)
                        expected_current = self.binary_search_first(current_array_copy, target)
                    else:
                        expected_original = self.binary_search(arr, target)
                        expected_current = self.binary_search(current_array_copy, target)

                    # 답변 확인
                    if user_answer == expected_original or user_answer == expected_current:
                        result_msg = f"✅ Correct! {'Found at index' if user_answer != -1 else 'Not in array'} {user_answer}\n"
                        await self.safe_write(writer, result_msg.encode(), client_id)
                        logging.info(f"Client {client_id} Room {room} Query {i + 1}: Correct")
                    else:
                        result_msg = f"❌ Wrong! Expected {expected_original} (original) or {expected_current} (current), got {user_answer}\n"
                        await self.safe_write(writer, result_msg.encode(), client_id)

                        # 디버그 정보
                        if expected_current != -1:
                            debug_msg = f"(Debug: Target {target} is at index {expected_current} in current array)\n"
                        elif expected_original != -1:
                            debug_msg = f"(Debug: Target {target} was at index {expected_original} in original array but may have been removed)\n"
                        else:
                            debug_msg = f"(Debug: Target {target} is not in the array)\n"

                        await self.safe_write(writer, debug_msg.encode(), client_id)
                        logging.info(f"Client {client_id} Room {room} Query {i + 1}: Wrong - Game Over")
                        return False

                except ValueError as e:
                    await self.safe_write(writer, f"❌ Invalid input: {e}\n".encode(), client_id)
                    logging.warning(f"Client {client_id} Invalid input: {e}")
                    return False
                except asyncio.TimeoutError:
                    await self.safe_write(writer, "❌ Timeout!\n".encode(), client_id)
                    logging.warning(f"Client {client_id} Timeout")
                    return False

            # 방 클리어
            await self.safe_write(writer, f"🎉 Room {room} cleared!\n".encode(), client_id)
            logging.info(f"Client {client_id} Room {room} cleared")
            return True

        finally:
            # 수정 작업 중지
            stop_event.set()
            modification_task.cancel()
            try:
                await modification_task
            except asyncio.CancelledError:
                pass

    async def readLine(self, reader):
        """타임아웃과 함께 한 줄 읽기"""
        data = await asyncio.wait_for(reader.readline(), timeout=self.CONNECTION_TIMEOUT)
        return data.decode()

    async def safe_write(self, writer, data: bytes, client_id: int) -> bool:
        """연결 확인과 함께 안전하게 데이터 쓰기"""
        try:
            if writer.transport and writer.transport.is_closing():
                logging.debug(f"Client {client_id} connection already closing, skipping write")
                return False

            writer.write(data)
            await writer.drain()
            return True

        except (BrokenPipeError, ConnectionResetError, OSError) as e:
            logging.debug(f"Client {client_id} connection lost during write: {e}")
            return False
        except Exception as e:
            logging.warning(f"Client {client_id} unexpected error during write: {e}")
            return False

    def binary_search(self, arr: List[int], target: int) -> int:
        """표준 이진 탐색 구현"""
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

    def binary_search_first(self, arr: List[int], target: int) -> int:
        """첫 번째 발생 위치를 찾는 이진 탐색"""
        left, right = 0, len(arr) - 1
        result = -1

        while left <= right:
            mid = (left + right) // 2
            if arr[mid] == target:
                result = mid
                right = mid - 1  # 왼쪽 계속 탐색
            elif arr[mid] < target:
                left = mid + 1
            else:
                right = mid - 1

        return result

    def validate_input(self, response: str, array_size: int) -> int:
        """사용자 입력 검증"""
        if len(response) > self.MAX_INPUT_LENGTH:
            raise ValueError(f"Input too long (max {self.MAX_INPUT_LENGTH} chars)")

        try:
            value = int(response)
        except ValueError:
            raise ValueError("Not a valid integer")

        if value < -1 or value >= array_size:
            raise ValueError(f"Invalid index (must be -1 to {array_size - 1})")

        return value

    def generate_room(self, level: int) -> Tuple[List[int], List[Tuple[int, QueryType]]]:
        """각 방에 대한 배열과 쿼리 생성"""
        config = self.ROOM_CONFIGS[level]
        size = random.randint(*config.size_range)

        if level == 1:
            # 중복 없는 간단한 정렬 배열
            arr = sorted(random.sample(range(*config.value_range), size))
            queries = []

            # 존재하는 값 2개와 존재하지 않는 값 1개
            present1 = random.choice(arr)
            present2 = random.choice([x for x in arr if x != present1])
            not_present = random.choice([x for x in range(*config.value_range) if x not in arr])

            queries = [
                (present1, QueryType.FIND),
                (present2, QueryType.FIND),
                (not_present, QueryType.FIND)
            ]
            random.shuffle(queries)

        elif level == 2:
            # 중간 크기 배열
            arr = sorted(random.sample(range(*config.value_range), size))
            queries = []

            # 존재하는 값 3개
            for _ in range(3):
                queries.append((random.choice(arr), QueryType.FIND))

            # 최댓값보다 큰 값 1개
            max_val = max(arr)
            queries.append((random.randint(max_val + 1, max_val + 100), QueryType.FIND))
            random.shuffle(queries)

        else:  # level 3
            # 중복을 포함한 큰 배열
            unique_vals = random.sample(range(*config.value_range), size // 2)
            arr = []
            for val in unique_vals:
                count = random.randint(1, 4)
                arr.extend([val] * count)
            arr = sorted(arr[:size])

            queries = []
            duplicates = [x for x in set(arr) if arr.count(x) > 1]

            # 중복값에 대한 "첫 번째 찾기" 쿼리 추가
            if duplicates:
                for _ in range(min(2, len(duplicates))):
                    if duplicates:
                        target = random.choice(duplicates)
                        queries.append((target, QueryType.FIND_FIRST))
                        duplicates.remove(target)

            # 나머지 쿼리 채우기
            used_targets = {q[0] for q in queries}
            available_elements = [x for x in arr if x not in used_targets]

            while len(queries) < config.queries:
                if available_elements and random.random() < 0.8:
                    target = random.choice(available_elements)
                    queries.append((target, QueryType.FIND))
                else:
                    max_val = max(arr)
                    target = random.randint(max_val + 1, max_val + 100)
                    queries.append((target, QueryType.FIND))

            random.shuffle(queries)

        return arr, queries

    async def apply_modification(self, writer, array: List[int],
                                 array_lock: asyncio.Lock, client_id: int) -> None:
        """배열에 무작위 수정 적용"""
        async with array_lock:
            if not array or len(array) == 0:
                return

            modification_type = random.choice(['insert', 'remove', 'modify'])

            try:
                if modification_type == 'insert':
                    new_value = random.randint(1, self.MAX_ARRAY_VALUE)

                    # 정렬 순서를 유지하기 위한 올바른 위치 찾기
                    insert_pos = 0
                    for i, val in enumerate(array):
                        if new_value <= val:
                            insert_pos = i
                            break
                    else:
                        insert_pos = len(array)

                    array.insert(insert_pos, new_value)
                    msg = f"🔄 ARRAY MODIFIED: INSERT at index {insert_pos} value {new_value}\n"
                    await self.safe_write(writer, msg.encode(), client_id)
                    logging.debug(f"Client {client_id} {msg.strip()}")

                elif modification_type == 'remove' and len(array) > self.MIN_ARRAY_SIZE:
                    remove_pos = random.randint(0, len(array) - 1)
                    removed_value = array.pop(remove_pos)
                    msg = f"🔄 ARRAY MODIFIED: REMOVE at index {remove_pos} (was {removed_value})\n"
                    await self.safe_write(writer, msg.encode(), client_id)
                    logging.debug(f"Client {client_id} {msg.strip()}")

                elif modification_type == 'modify':
                    modify_pos = random.randint(0, len(array) - 1)
                    old_value = array[modify_pos]
                    new_value = random.randint(1, self.MAX_ARRAY_VALUE)

                    # 기존 값 제거
                    array.pop(modify_pos)

                    # 새 값을 올바른 위치에 삽입
                    insert_pos = 0
                    for i, val in enumerate(array):
                        if new_value <= val:
                            insert_pos = i
                            break
                    else:
                        insert_pos = len(array)

                    array.insert(insert_pos, new_value)
                    msg = f"🔄 ARRAY MODIFIED: MODIFY at index {modify_pos} from {old_value} to {new_value} (now at index {insert_pos})\n"
                    await self.safe_write(writer, msg.encode(), client_id)
                    logging.debug(f"Client {client_id} {msg.strip()}")

            except Exception as e:
                logging.error(f"Client {client_id} error applying modification: {e}")

    async def modification_task(self, writer, array: List[int],
                                array_lock: asyncio.Lock, interval: float,
                                client_id: int, stop_event: asyncio.Event) -> None:
        """주기적으로 배열 수정"""
        logging.info(f"Client {client_id} modification task started (interval: {interval}s)")

        try:
            while not stop_event.is_set():
                await asyncio.sleep(interval)
                if stop_event.is_set():
                    break
                await self.apply_modification(writer, array, array_lock, client_id)
        except asyncio.CancelledError:
            logging.debug(f"Client {client_id} modification task cancelled")
        except Exception as e:
            logging.error(f"Client {client_id} modification task error: {e}")
        finally:
            logging.info(f"Client {client_id} modification task ended")


if __name__ == '__main__':
    server = ProblemServer(host='0.0.0.0', port=10437)
    asyncio.run(server.run())