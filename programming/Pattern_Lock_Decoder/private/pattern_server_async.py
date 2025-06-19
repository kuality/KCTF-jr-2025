#!/usr/bin/env python3
import asyncio
import random
import logging
from typing import Tuple

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class ProblemServer:
    FLAG = "KCTF_Jr{1cs_p4tt3rn_m4st3r_2025}"
    DNA_BASES = 'ACGT'
    MAX_CONNECTIONS = 50
    CONNECTION_TIMEOUT = 60

    # Time limits for each level (in seconds)
    TIME_LIMITS = {1: 30, 2: 20, 3: 15, 4: 10}

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.active_connections = 0
        self.connection_semaphore = asyncio.Semaphore(self.MAX_CONNECTIONS)

    async def run(self):
        server = await asyncio.start_server(self.on_connect, host=self.host, port=self.port)
        logging.info(f"Pattern Lock Decoder server started on {self.host}:{self.port}")
        logging.info(f"Maximum concurrent connections: {self.MAX_CONNECTIONS}")
        await server.wait_closed()

    async def on_connect(self, reader, writer):
        peername = writer.get_extra_info('peername')

        async with self.connection_semaphore:
            self.active_connections += 1
            logging.info(f"Client connected: {peername}")
            logging.info(f"Active connections: {self.active_connections}")

            def cleanup(fu):
                try:
                    fu.result()
                except Exception as e:
                    logging.error(f"Exception in client connection: {e}")

                self.active_connections -= 1
                logging.info(f"Client disconnected: {peername}")
                logging.info(f"Active connections: {self.active_connections}")

            task = asyncio.create_task(self.handle_client(reader, writer))
            task.add_done_callback(cleanup)

    async def handle_client(self, reader, writer):
        try:
            await asyncio.wait_for(self.handle_problem(reader, writer),
                                   timeout=self.CONNECTION_TIMEOUT)
        except asyncio.TimeoutError:
            logging.warning("Client connection timed out.")
            writer.write("Connection timed out\r\n".encode())
            writer.close()
            await writer.wait_closed()

    async def handle_problem(self, reader, writer):
        # Welcome message
        welcome = """
=== Pattern Lock Decoder - SPEED CHALLENGE ===
The vault uses DNA pattern locks based on Longest Common Subsequence!
Find the LCS length between two DNA sequences to unlock each level.

⚡ WARNING: Each level has a TIME LIMIT! ⚡
The timer gets shorter as you progress!

DNA sequences use bases: A, C, G, T
You need to solve 4 pattern locks to get the flag.
Format your answer as a single integer (LCS length).
"""
        writer.write(welcome.encode())
        await writer.drain()

        # Process each level
        for level in range(1, 5):
            writer.write(f"\n--- Lock Level {level} ---\n".encode())
            writer.write(f"⏰ TIME LIMIT: {self.TIME_LIMITS[level]} seconds!\n".encode())
            await writer.drain()

            # Generate challenge
            seq1, seq2 = self.generate_challenge(level)
            expected = self.longest_common_subsequence(seq1, seq2)

            # Send challenge
            challenge = f"DNA Sequence 1: {seq1}\n"
            challenge += f"DNA Sequence 2: {seq2}\n"
            challenge += f"LCS Length: "

            writer.write(challenge.encode())
            await writer.drain()

            try:
                # Wait for response with timeout
                start_time = asyncio.get_event_loop().time()
                response = await asyncio.wait_for(
                    self.readLine(reader),
                    timeout=self.TIME_LIMITS[level]
                )
                elapsed_time = asyncio.get_event_loop().time() - start_time

                user_answer = int(response.strip())

                if user_answer == expected:
                    writer.write(f"\n✅ Lock opened in {elapsed_time:.1f} seconds! LCS length is {expected}\n".encode())

                    # Bonus message for fast solvers
                    if elapsed_time < self.TIME_LIMITS[level] * 0.5:
                        writer.write(
                            f"🌟 AMAZING SPEED! You used only {int(elapsed_time / self.TIME_LIMITS[level] * 100)}% of the time!\n".encode()
                        )
                    await writer.drain()
                    logging.info(f"Level {level}: Correct answer in {elapsed_time:.1f}s")
                else:
                    writer.write(f"\n❌ Lock failed! Expected {expected}, got {user_answer}\n".encode())
                    await writer.drain()
                    logging.info(f"Level {level}: Wrong answer")
                    writer.close()
                    await writer.wait_closed()
                    return

            except asyncio.TimeoutError:
                writer.write(f"\n❌ TIME'S UP! No answer received within {self.TIME_LIMITS[level]} seconds!\n".encode())
                await writer.drain()
                logging.warning(f"Level {level}: Timeout")
                writer.close()
                await writer.wait_closed()
                return
            except ValueError:
                writer.write("\n❌ Invalid input format!\n".encode())
                await writer.drain()
                logging.warning(f"Level {level}: Invalid input")
                writer.close()
                await writer.wait_closed()
                return

        # All locks opened
        writer.write(f"\n🎉 ALL LOCKS CRACKED! Here's your flag: {self.FLAG}\n".encode())
        writer.write("You're a true speed solver!\n".encode())
        await writer.drain()
        logging.info("All levels completed! Flag delivered!")

        writer.close()
        await writer.wait_closed()

    async def readLine(self, reader):
        """Read a line from the reader"""
        data = await reader.readline()
        return data.decode()

    def generate_dna_sequence(self, length: int) -> str:
        """Generate random DNA sequence"""
        return ''.join(random.choice(self.DNA_BASES) for _ in range(length))

    def generate_challenge(self, level: int) -> Tuple[str, str]:
        """Generate DNA sequences based on difficulty"""
        if level == 1:
            # Short sequences
            len1 = random.randint(8, 12)
            len2 = random.randint(8, 12)
        elif level == 2:
            # Medium sequences
            len1 = random.randint(15, 25)
            len2 = random.randint(15, 25)
        elif level == 3:
            # Long sequences
            len1 = random.randint(30, 40)
            len2 = random.randint(30, 40)
        else:  # level 4
            # Very long sequences
            len1 = random.randint(50, 70)
            len2 = random.randint(50, 70)

        seq1 = self.generate_dna_sequence(len1)
        seq2 = self.generate_dna_sequence(len2)

        return seq1, seq2

    def longest_common_subsequence(self, s1: str, s2: str) -> int:
        """Calculate LCS length using dynamic programming"""
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i - 1] == s2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

        return dp[m][n]


if __name__ == '__main__':
    server = ProblemServer(host='0.0.0.0', port=10402)
    asyncio.run(server.run())