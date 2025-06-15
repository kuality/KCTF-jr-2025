#!/usr/bin/env python3
import asyncio
import os
import random
import logging
import socket
from typing import List, Tuple, Optional
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Query type enumeration"""
    FIND = 'find'
    FIND_FIRST = 'first'


class RoomConfig:
    """Configuration for each room level"""
    def __init__(self, size_range: Tuple[int, int], value_range: Tuple[int, int],
                 queries: int, modification_interval: float):
        self.size_range = size_range
        self.value_range = value_range
        self.queries = queries
        self.modification_interval = modification_interval


class MazeServer:
    # Constants
    MAX_INPUT_LENGTH = 20
    MIN_ARRAY_SIZE = 10
    MAX_ARRAY_VALUE = 2000
    CONNECTION_TIMEOUT = 240  # 4 minutes
    MAX_CONNECTIONS = 50

    # Room configurations
    ROOM_CONFIGS = {
        1: RoomConfig((10, 100), (1, 1000), 3, 3.0),
        2: RoomConfig((100, 1000), (1, 10000), 4, 1.0),
        3: RoomConfig((1000, 10000), (1, 100000), 100, 1.0)
    }

    def __init__(self):
        self.host: str = os.environ.get('HOST', '0.0.0.0')
        self.port: int = int(os.environ.get('PORT', '9004'))
        self.flag: str = os.environ.get('FLAG', 'kctf-jr{binary_search_speedrunner_2025}')
        self.active_connections: int = 0
        self.total_connections: int = 0
        self.connection_semaphore: asyncio.Semaphore = asyncio.Semaphore(self.MAX_CONNECTIONS)

    def initialize(self):
        """Initialize server resources"""
        logger.info(f"Binary Maze Runner server initialized")
        logger.info(f"Flag loaded: {'*' * len(self.flag)}")
        logger.info(f"Maximum concurrent connections: {self.MAX_CONNECTIONS}")

        # Verify flag format
        if not self.flag.startswith(('kctf-jr{', 'flag{', 'CTF{')) or not self.flag.endswith('}'):
            logger.warning(f"Flag format may be incorrect: {self.flag}")
        else:
            logger.info("Flag format validation passed")

    def binary_search(self, arr: List[int], target: int) -> int:
        """Standard binary search implementation"""
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
        """Binary search to find first occurrence"""
        left, right = 0, len(arr) - 1
        result = -1

        while left <= right:
            mid = (left + right) // 2
            if arr[mid] == target:
                result = mid
                right = mid - 1  # Continue searching left
            elif arr[mid] < target:
                left = mid + 1
            else:
                right = mid - 1

        return result

    def generate_room(self, level: int) -> Tuple[List[int], List[Tuple[int, QueryType]]]:
        """Generate array and queries for each room"""
        config = self.ROOM_CONFIGS[level]
        size = random.randint(*config.size_range)

        if level == 1:
            # Simple sorted array without duplicates
            arr = sorted(random.sample(range(*config.value_range), size))
            queries = []

            # Two present values and one absent
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
            # Medium array
            arr = sorted(random.sample(range(*config.value_range), size))
            queries = []

            # Three present values
            for _ in range(3):
                queries.append((random.choice(arr), QueryType.FIND))

            # One value larger than max
            max_val = max(arr)
            queries.append((random.randint(max_val + 1, max_val + 100), QueryType.FIND))
            random.shuffle(queries)

        else:  # level 3
            # Large array with duplicates
            unique_vals = random.sample(range(*config.value_range), size // 2)
            arr = []
            for val in unique_vals:
                count = random.randint(1, 4)
                arr.extend([val] * count)
            arr = sorted(arr[:size])

            queries = []
            duplicates = [x for x in set(arr) if arr.count(x) > 1]

            # Add some "find first" queries for duplicates
            if duplicates:
                for _ in range(min(2, len(duplicates))):
                    if duplicates:
                        target = random.choice(duplicates)
                        queries.append((target, QueryType.FIND_FIRST))
                        duplicates.remove(target)

            # Fill remaining queries
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

    async def apply_modification(self, writer: asyncio.StreamWriter, array: List[int],
                                array_lock: asyncio.Lock, client_id: int) -> None:
        """Apply random modification to the array"""
        async with array_lock:
            if not array or len(array) == 0:
                return

            modification_type = random.choice(['insert', 'remove', 'modify'])

            try:
                if modification_type == 'insert':
                    new_value = random.randint(1, self.MAX_ARRAY_VALUE)

                    # Find correct position to maintain sorted order
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
                    logger.debug(f"[Client {client_id}] {msg.strip()}")

                elif modification_type == 'remove' and len(array) > self.MIN_ARRAY_SIZE:
                    remove_pos = random.randint(0, len(array) - 1)
                    removed_value = array.pop(remove_pos)
                    msg = f"🔄 ARRAY MODIFIED: REMOVE at index {remove_pos} (was {removed_value})\n"
                    await self.safe_write(writer, msg.encode(), client_id)
                    logger.debug(f"[Client {client_id}] {msg.strip()}")

                elif modification_type == 'modify':
                    modify_pos = random.randint(0, len(array) - 1)
                    old_value = array[modify_pos]
                    new_value = random.randint(1, self.MAX_ARRAY_VALUE)

                    # Remove old value
                    array.pop(modify_pos)

                    # Insert new value in correct position
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
                    logger.debug(f"[Client {client_id}] {msg.strip()}")

            except Exception as e:
                logger.error(f"[Client {client_id}] Error applying modification: {e}")

    async def modification_task(self, writer: asyncio.StreamWriter, array: List[int],
                               array_lock: asyncio.Lock, interval: float,
                               client_id: int, stop_event: asyncio.Event) -> None:
        """Periodically modify the array"""
        logger.info(f"[Client {client_id}] Modification task started (interval: {interval}s)")

        try:
            while not stop_event.is_set():
                await asyncio.sleep(interval)
                if stop_event.is_set():
                    break
                await self.apply_modification(writer, array, array_lock, client_id)
        except asyncio.CancelledError:
            logger.debug(f"[Client {client_id}] Modification task cancelled")
        except Exception as e:
            logger.error(f"[Client {client_id}] Modification task error: {e}")
        finally:
            logger.info(f"[Client {client_id}] Modification task ended")

    def validate_input(self, response: str, array_size: int) -> int:
        """Validate user input"""
        if len(response) > self.MAX_INPUT_LENGTH:
            raise ValueError(f"Input too long (max {self.MAX_INPUT_LENGTH} chars)")

        try:
            value = int(response)
        except ValueError:
            raise ValueError("Not a valid integer")

        if value < -1 or value >= array_size:
            raise ValueError(f"Invalid index (must be -1 to {array_size - 1})")

        return value

    async def safe_write(self, writer: asyncio.StreamWriter, data: bytes, client_id: int) -> bool:
        """Safely write data to client with connection checking"""
        try:
            # Check if connection is still open
            if writer.transport and writer.transport.is_closing():
                logger.debug(f"[Client {client_id}] Connection already closing, skipping write")
                return False

            writer.write(data)
            await writer.drain()
            return True

        except (BrokenPipeError, ConnectionResetError, OSError) as e:
            logger.debug(f"[Client {client_id}] Connection lost during write: {e}")
            return False
        except Exception as e:
            logger.warning(f"[Client {client_id}] Unexpected error during write: {e}")
            return False

    def is_connection_open(self, writer: asyncio.StreamWriter) -> bool:
        """Check if connection is still open"""
        return writer.transport and not writer.transport.is_closing()

    async def handle_room(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter,
                         room: int, client_id: int) -> bool:
        """Handle a single room challenge"""
        logger.info(f"[Client {client_id}] Starting Room {room}")

        if not await self.safe_write(writer, f"\n--- Room {room} ---\n".encode(), client_id):
            return False

        # Generate room data
        arr, queries = self.generate_room(room)
        current_array = arr[:]
        array_lock = asyncio.Lock()

        # Send array
        if not await self.safe_write(writer, f"Array (size={len(arr)}): {arr}\n\n".encode(), client_id):
            return False

        # Start modification task
        config = self.ROOM_CONFIGS[room]
        stop_event = asyncio.Event()
        modification_task = asyncio.create_task(
            self.modification_task(writer, current_array, array_lock,
                                 config.modification_interval, client_id, stop_event)
        )

        try:
            # Process each query
            for i, (target, query_type) in enumerate(queries):
                if query_type == QueryType.FIND_FIRST:
                    query_msg = f"Query {i + 1}: Find FIRST occurrence of {target}\nIndex: "
                else:
                    query_msg = f"Query {i + 1}: Find {target}\nIndex: "

                if not await self.safe_write(writer, query_msg.encode(), client_id):
                    return False

                try:
                    # Read answer with timeout
                    response_data = await asyncio.wait_for(
                        reader.readline(),
                        timeout=self.CONNECTION_TIMEOUT
                    )
                    response = response_data.decode().strip()

                    # Check current array state
                    async with array_lock:
                        array_size = len(current_array)
                        current_array_copy = current_array[:]

                    # Validate input
                    user_answer = self.validate_input(response, array_size)

                    # Calculate expected answers
                    if query_type == QueryType.FIND_FIRST:
                        expected_original = self.binary_search_first(arr, target)
                        expected_current = self.binary_search_first(current_array_copy, target)
                    else:
                        expected_original = self.binary_search(arr, target)
                        expected_current = self.binary_search(current_array_copy, target)

                    # Check answer
                    if user_answer == expected_original or user_answer == expected_current:
                        result_msg = f"✅ Correct! {'Found at index' if user_answer != -1 else 'Not in array'} {user_answer}\n"
                        await self.safe_write(writer, result_msg.encode(), client_id)
                        logger.info(f"[Client {client_id}] Room {room} Query {i + 1}: Correct")
                    else:
                        result_msg = f"❌ Wrong! Expected {expected_original} (original) or {expected_current} (current), got {user_answer}\n"
                        await self.safe_write(writer, result_msg.encode(), client_id)

                        # Debug info
                        if expected_current != -1:
                            debug_msg = f"(Debug: Target {target} is at index {expected_current} in current array)\n"
                        elif expected_original != -1:
                            debug_msg = f"(Debug: Target {target} was at index {expected_original} in original array but may have been removed)\n"
                        else:
                            debug_msg = f"(Debug: Target {target} is not in the array)\n"

                        await self.safe_write(writer, debug_msg.encode(), client_id)
                        logger.info(f"[Client {client_id}] Room {room} Query {i + 1}: Wrong - Game Over")
                        return False

                except ValueError as e:
                    await self.safe_write(writer, f"❌ Invalid input: {e}\n".encode(), client_id)
                    logger.warning(f"[Client {client_id}] Invalid input: {e}")
                    return False
                except asyncio.TimeoutError:
                    await self.safe_write(writer, "❌ Timeout!\n".encode(), client_id)
                    logger.warning(f"[Client {client_id}] Timeout")
                    return False

            # Room cleared
            await self.safe_write(writer, f"🎉 Room {room} cleared!\n".encode(), client_id)
            logger.info(f"[Client {client_id}] Room {room} cleared")
            return True

        finally:
            # Stop modification task
            stop_event.set()
            modification_task.cancel()
            try:
                await modification_task
            except asyncio.CancelledError:
                pass


    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle a client connection"""
        addr = writer.get_extra_info('peername')

        async with self.connection_semaphore:
            self.active_connections += 1
            self.total_connections += 1
            client_id = self.total_connections

            logger.info(f"[Client {client_id}] Connected from {addr}")
            logger.info(f"Active connections: {self.active_connections}")

            try:
                # Welcome message
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
                    logger.info(f"[Client {client_id}] Failed to send welcome message")
                    return

                # Small delay to ensure client is ready
                await asyncio.sleep(0.1)

                # Process all 3 rooms
                for room in range(1, 4):
                    success = await self.handle_room(reader, writer, room, client_id)
                    if not success:
                        logger.info(f"[Client {client_id}] Failed at room {room}")
                        return

                # All rooms cleared - send flag
                logger.info(f"[Client {client_id}] All rooms completed! Sending flag: {self.flag[:15]}...{self.flag[-5:]}")
                flag_message = f"\n🎉 MAZE COMPLETED! Here's your flag: {self.flag}\n"
                await self.safe_write(writer, flag_message.encode(), client_id)
                await self.safe_write(writer, b"Congratulations, Binary Search Master!\n", client_id)
                logger.info(f"[Client {client_id}] Flag delivered successfully!")

            except asyncio.TimeoutError:
                logger.warning(f"[Client {client_id}] Connection timeout")
                await self.safe_write(writer, "\n❌ Connection timeout!\n".encode(), client_id)

            except (BrokenPipeError, ConnectionResetError, socket.error) as e:
                logger.warning(f"[Client {client_id}] Disconnected unexpectedly: {e}")

            except Exception as e:
                logger.error(f"[Client {client_id}] Unexpected error: {e}")

            finally:
                self.active_connections -= 1
                try:
                    if not writer.transport.is_closing():
                        writer.close()
                        await writer.wait_closed()
                except Exception as e:
                    logger.debug(f"[Client {client_id}] Exception during cleanup: {e}")
                logger.info(f"[Client {client_id}] Disconnected. Active connections: {self.active_connections}")

    async def listen_forever(self):
        """Start the server and listen for connections"""
        server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port
        )

        addr = server.sockets[0].getsockname()
        logger.info(f"Binary Maze Runner server listening on {addr[0]}:{addr[1]}")
        logger.info(f"Maximum concurrent connections: {self.MAX_CONNECTIONS}")

        async with server:
            await server.serve_forever()

    async def shutdown(self):
        """Graceful shutdown handler"""
        logger.info("Server shutting down...")
        logger.info(f"Total connections served: {self.total_connections}")
        logger.info(f"Active connections: {self.active_connections}")


async def main():
    """Main entry point"""
    server = MazeServer()
    server.initialize()
    
    # Setup graceful shutdown
    loop = asyncio.get_event_loop()
    
    def signal_handler():
        asyncio.create_task(server.shutdown())
        loop.stop()
    
    # Register signal handlers
    try:
        import signal
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, signal_handler)
    except NotImplementedError:
        # Signal handling not available on Windows
        pass
    
    try:
        await server.listen_forever()
    except asyncio.CancelledError:
        logger.info("Server stopped")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")