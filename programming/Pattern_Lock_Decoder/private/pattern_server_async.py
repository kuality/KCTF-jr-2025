#!/usr/bin/env python3
import asyncio
import os
import random
import logging
import socket
import sys
import argparse
import signal
import psutil
from typing import Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PatternServer:
    def __init__(self):
        self.host: str = os.environ.get('HOST', '0.0.0.0')
        self.port: int = int(os.environ.get('PORT', '39991'))
        self.flag: str = os.environ.get('FLAG', 'KCTF_Jr{1cs_p4tt3rn_m4st3r_2025}')
        self.dna_bases: str = 'ACGT'
        self.max_connections: int = 100
        self.active_connections: int = 0
        self.connection_semaphore: asyncio.Semaphore = asyncio.Semaphore(self.max_connections)
        self.server: Optional[asyncio.Server] = None
        self.pid_file: str = '/tmp/pattern_server.pid'
        self.port_range: Tuple[int, int] = (9003, 9010)

    def initialize(self):
        """Initialize server resources"""
        logger.info(f"Pattern Lock Decoder server initialized")
        logger.info(f"Flag loaded: {'*' * len(self.flag)}")

    def generate_dna_sequence(self, length: int) -> str:
        """Generate random DNA sequence"""
        return ''.join(random.choice(self.dna_bases) for _ in range(length))

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

    def check_port_availability(self, port: int) -> bool:
        """Check if a port is available for binding"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((self.host, port))
            return True
        except OSError:
            return False
        finally:
            try:
                sock.close()
            except:
                pass

    def find_process_using_port(self, port: int) -> Optional[int]:
        """Find the PID of the process using a specific port"""
        try:
            for conn in psutil.net_connections():
                if conn.laddr and conn.laddr.port == port:
                    return conn.pid
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass
        return None

    def find_available_port(self) -> Optional[int]:
        """Find an available port within the specified range"""
        start_port, end_port = self.port_range

        for port in range(start_port, end_port + 1):
            logger.info(f"Checking port {port}...")
            if self.check_port_availability(port):
                return port
            else:
                pid = self.find_process_using_port(port)
                if pid:
                    try:
                        process = psutil.Process(pid)
                        logger.warning(f"Port {port} is in use by process: {process.name()} (PID: {pid})")
                    except psutil.NoSuchProcess:
                        logger.warning(f"Port {port} is in use by PID: {pid}")
                else:
                    logger.warning(f"Port {port} is in use by unknown process")

        return None

    def write_pid_file(self):
        """Write current PID to file"""
        try:
            with open(self.pid_file, 'w') as f:
                f.write(str(os.getpid()))
            logger.debug(f"PID file written: {self.pid_file}")
        except Exception as e:
            logger.warning(f"Could not write PID file: {e}")

    def remove_pid_file(self):
        """Remove PID file"""
        try:
            if os.path.exists(self.pid_file):
                os.remove(self.pid_file)
                logger.debug(f"PID file removed: {self.pid_file}")
        except Exception as e:
            logger.warning(f"Could not remove PID file: {e}")

    def check_existing_instance(self) -> Optional[int]:
        """Check if another instance is already running"""
        try:
            if os.path.exists(self.pid_file):
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())

                # Check if process is still running
                if psutil.pid_exists(pid):
                    return pid
                else:
                    # Stale PID file, remove it
                    self.remove_pid_file()
        except Exception:
            pass

        return None

    async def countdown_timer(self, writer: asyncio.StreamWriter, time_limit: int,
                            level_complete: asyncio.Event) -> bool:
        """Send countdown updates to client"""
        start_time = asyncio.get_event_loop().time()
        last_update = start_time

        try:
            while asyncio.get_event_loop().time() - start_time < time_limit:
                if level_complete.is_set():
                    return True

                current_time = asyncio.get_event_loop().time()
                elapsed = current_time - start_time
                remaining = time_limit - elapsed

                # Send update every second
                if current_time - last_update >= 1:
                    try:
                        writer.write(f"\r⏰ Time remaining: {int(remaining)} seconds...".encode())
                        await writer.drain()
                        last_update = current_time
                    except Exception:
                        break

                await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            pass

        return False

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle a client connection"""
        addr = writer.get_extra_info('peername')
        logger.info(f"New connection from {addr}")

        async with self.connection_semaphore:
            self.active_connections += 1
            try:
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

                # Time limits for each level (in seconds)
                time_limits = {1: 30, 2: 20, 3: 15, 4: 10}

                for level in range(1, 5):
                    writer.write(f"\n--- Lock Level {level} ---\n".encode())
                    writer.write(f"⏰ TIME LIMIT: {time_limits[level]} seconds!\n".encode())
                    await writer.drain()

                    seq1, seq2 = self.generate_challenge(level)
                    expected = self.longest_common_subsequence(seq1, seq2)

                    challenge = f"DNA Sequence 1: {seq1}\n"
                    challenge += f"DNA Sequence 2: {seq2}\n"
                    challenge += f"LCS Length: "

                    writer.write(challenge.encode())
                    await writer.drain()

                    # Start countdown timer
                    level_complete = asyncio.Event()
                    timer_task = asyncio.create_task(
                        self.countdown_timer(writer, time_limits[level], level_complete)
                    )

                    try:
                        # Wait for response with timeout
                        start_time = asyncio.get_event_loop().time()
                        response_data = await asyncio.wait_for(
                            reader.readline(),
                            timeout=time_limits[level]
                        )
                        elapsed_time = asyncio.get_event_loop().time() - start_time

                        # Signal timer task that level is complete
                        level_complete.set()
                        timer_task.cancel()
                        await asyncio.gather(timer_task, return_exceptions=True)

                        response = response_data.decode().strip()
                        user_answer = int(response)

                        if user_answer == expected:
                            writer.write(f"\n✅ Lock opened in {elapsed_time:.1f} seconds! LCS length is {expected}\n".encode())

                            # Bonus message for fast solvers
                            if elapsed_time < time_limits[level] * 0.5:
                                writer.write(
                                    f"🌟 AMAZING SPEED! You used only {int(elapsed_time / time_limits[level] * 100)}% of the time!\n".encode()
                                )
                            await writer.drain()
                        else:
                            writer.write(f"\n❌ Lock failed! Expected {expected}, got {user_answer}\n".encode())
                            await writer.drain()
                            logger.info(f"Client {addr} failed at level {level}")
                            return

                    except asyncio.TimeoutError:
                        level_complete.set()
                        timer_task.cancel()
                        await asyncio.gather(timer_task, return_exceptions=True)
                        writer.write(f"\n❌ TIME'S UP! No answer received within {time_limits[level]} seconds!\n".encode())
                        await writer.drain()
                        logger.info(f"Client {addr} timed out at level {level}")
                        return
                    except ValueError:
                        level_complete.set()
                        timer_task.cancel()
                        await asyncio.gather(timer_task, return_exceptions=True)
                        writer.write("\n❌ Invalid input format!\n".encode())
                        await writer.drain()
                        logger.info(f"Client {addr} sent invalid input at level {level}")
                        return
                    except Exception as e:
                        level_complete.set()
                        timer_task.cancel()
                        await asyncio.gather(timer_task, return_exceptions=True)
                        logger.error(f"Error in level {level} for client {addr}: {e}")
                        return

                # All locks opened
                writer.write(f"\n🎉 ALL LOCKS CRACKED! Here's your flag: {self.flag}\n".encode())
                writer.write(f"You're a true speed solver!\n".encode())
                await writer.drain()
                logger.info(f"Client {addr} successfully completed all levels!")

            except Exception as e:
                logger.error(f"Error handling client {addr}: {e}")
            finally:
                self.active_connections -= 1
                writer.close()
                await writer.wait_closed()
                logger.info(f"Connection closed for {addr}. Active connections: {self.active_connections}")

    async def start_server_on_port(self, port: int) -> Optional[asyncio.Server]:
        """Attempt to start server on a specific port"""
        try:
            logger.info(f"Attempting to bind to {self.host}:{port}...")

            # Create server with SO_REUSEADDR
            server = await asyncio.start_server(
                self.handle_client,
                self.host,
                port,
                reuse_address=True,
                reuse_port=True if sys.platform != 'win32' else False
            )

            logger.info(f"✅ Successfully bound to {self.host}:{port}")
            return server

        except OSError as e:
            if e.errno == 48 or e.errno == 98:  # Address already in use
                logger.warning(f"❌ Port {port} is already in use")

                # Try to find which process is using it
                pid = self.find_process_using_port(port)
                if pid:
                    try:
                        process = psutil.Process(pid)
                        logger.info(f"   Process using port: {process.name()} (PID: {pid})")
                        logger.info(f"   Command: {' '.join(process.cmdline())}")
                    except psutil.NoSuchProcess:
                        logger.info(f"   Process using port: PID {pid}")
            else:
                logger.error(f"Failed to bind to port {port}: {e}")

            return None

    async def listen_forever(self):
        """Start the server and listen for connections"""
        # Check for existing instance
        existing_pid = self.check_existing_instance()
        if existing_pid:
            logger.warning(f"Another instance may be running (PID: {existing_pid})")
            logger.info("Use --force to override")

        # Try to bind to the preferred port first
        self.server = await self.start_server_on_port(self.port)

        # If preferred port fails, try alternative ports
        if not self.server:
            logger.info(f"Trying alternative ports {self.port_range[0]}-{self.port_range[1]}...")
            available_port = self.find_available_port()

            if available_port:
                self.server = await self.start_server_on_port(available_port)
                if self.server:
                    self.port = available_port

            if not self.server:
                logger.error(f"❌ Could not bind to any port in range {self.port_range[0]}-{self.port_range[1]}")
                logger.info("\nPossible solutions:")
                logger.info("1. Kill the process using the port: kill <PID>")
                logger.info("2. Use a different port: PORT=9005 python server.py")
                logger.info("3. Wait for the port to become available")
                raise RuntimeError("No available ports found")

        # Write PID file
        self.write_pid_file()

        addr = self.server.sockets[0].getsockname()
        logger.info(f"🚀 Pattern Lock Decoder server listening on {addr[0]}:{addr[1]}")
        logger.info(f"Maximum concurrent connections: {self.max_connections}")
        logger.info(f"PID: {os.getpid()}")

        async with self.server:
            await self.server.serve_forever()

    async def health_check(self):
        """Simple health check endpoint"""
        return {"status": "healthy", "active_connections": self.active_connections}

    async def shutdown(self):
        """Graceful shutdown handler"""
        logger.info("🛑 Server shutting down...")
        logger.info(f"Final active connections: {self.active_connections}")

        # Close the server
        if self.server:
            self.server.close()
            await self.server.wait_closed()

        # Remove PID file
        self.remove_pid_file()


async def main(args):
    """Main entry point"""
    # Override port if specified via command line
    if args.port:
        os.environ['PORT'] = str(args.port)

    server = PatternServer()
    server.initialize()

    # Setup graceful shutdown
    loop = asyncio.get_event_loop()
    shutdown_event = asyncio.Event()

    async def shutdown_handler():
        logger.info("Received shutdown signal")
        await server.shutdown()
        shutdown_event.set()

    # Register signal handlers for graceful shutdown
    if sys.platform != 'win32':
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(
                sig,
                lambda: asyncio.create_task(shutdown_handler())
            )

    try:
        await server.listen_forever()
    except asyncio.CancelledError:
        logger.info("Server stopped")
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
        await server.shutdown()
    except Exception as e:
        logger.error(f"Server error: {e}")
        await server.shutdown()
        raise


if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Pattern Lock Decoder CTF Server')
    parser.add_argument('--port', '-p', type=int, help='Port to bind to')
    parser.add_argument('--force', '-f', action='store_true', 
                        help='Force start even if another instance is running')
    args = parser.parse_args()
    
    try:
        asyncio.run(main(args))
    except RuntimeError as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
        sys.exit(0)