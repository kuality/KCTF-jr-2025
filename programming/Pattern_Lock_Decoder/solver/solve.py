#!/usr/bin/env python3
import socket
import time
import sys
import re
import logging
from typing import Optional, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class PatternLockSolver:
    def __init__(self, host='localhost', port=10402):
        """Pattern Lock Decoder client initialization"""
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        """Connect to the server"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        # Set socket timeout to prevent blocking
        self.sock.settimeout(0.1)
        logging.info(f"Connected to Pattern Lock Decoder server at {self.host}:{self.port}")

    def lcs_length_optimized(self, s1: str, s2: str) -> int:
        """Optimized LCS using space-efficient DP"""
        m, n = len(s1), len(s2)

        # Use only two rows instead of full matrix to save memory
        prev = [0] * (n + 1)
        curr = [0] * (n + 1)

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i - 1] == s2[j - 1]:
                    curr[j] = prev[j - 1] + 1
                else:
                    curr[j] = max(prev[j], curr[j - 1])
            prev, curr = curr, prev

        return prev[n]

    def receive_data(self, size=4096):
        """Receive data from socket"""
        return self.sock.recv(size).decode('utf-8', errors='ignore')

    def receive_until_pattern(self, patterns, timeout=10):
        """Receive data until one of the patterns is found"""
        buffer = ""
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                new_data = self.receive_data()
                if not new_data:
                    break
                buffer += new_data

                # Clean buffer for pattern matching (remove timer updates)
                clean_buffer = re.sub(r'\r⏰[^\n]*', '', buffer)

                # Check if any pattern matches in clean buffer
                for pattern in patterns:
                    if pattern in clean_buffer:
                        return buffer

            except socket.timeout:
                continue
            except Exception as e:
                logging.debug(f"Error receiving data: {e}")
                break

        return buffer

    def extract_sequences(self, data: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract DNA sequences from challenge data"""
        # Clean the data by removing timer updates
        clean_data = re.sub(r'\r⏰[^\n]*', '', data)

        seq1_match = re.search(r'DNA Sequence 1: ([ACGT]+)', clean_data)
        seq2_match = re.search(r'DNA Sequence 2: ([ACGT]+)', clean_data)

        seq1 = seq1_match.group(1) if seq1_match else None
        seq2 = seq2_match.group(1) if seq2_match else None

        return seq1, seq2

    def clean_display_text(self, text: str) -> str:
        """Clean text for display by removing timer updates"""
        lines = []
        for line in text.split('\n'):
            # Skip timer updates and carriage return lines
            if not line.strip().startswith('⏰') and not line.strip().startswith('\r⏰'):
                lines.append(line.rstrip('\r'))
        return '\n'.join(lines)

    def solve(self):
        """Main solving logic"""
        try:
            self.connect()

            # Receive welcome message
            welcome_buffer = self.receive_until_pattern(["Format your answer as a single integer (LCS length)."],
                                                        timeout=10)
            logging.info("Game Started")
            clean_welcome = self.clean_display_text(welcome_buffer)
            logging.debug(clean_welcome)

            # Process each level
            for level in range(1, 5):
                logging.info(f"Starting Level {level}")

                # Wait for level challenge - look for "LCS Length: " prompt
                challenge_buffer = self.receive_until_pattern(["LCS Length: "], timeout=40)

                # Extract sequences from the raw buffer (before cleaning)
                seq1, seq2 = self.extract_sequences(challenge_buffer)

                if not seq1 or not seq2:
                    logging.error(f"Could not extract sequences!")
                    logging.debug(f"Raw data: {challenge_buffer[-200:]}")
                    return

                logging.info(f"Sequence 1 length: {len(seq1)}, Sequence 2 length: {len(seq2)}")

                # Calculate LCS with timing
                calc_start = time.time()
                answer = self.lcs_length_optimized(seq1, seq2)
                calc_time = time.time() - calc_start

                logging.info(f"Calculated LCS: {answer} (in {calc_time:.3f}s)")

                # Send answer immediately
                self.sock.send(f"{answer}\n".encode())
                logging.debug("Answer sent!")

                # Receive response - wait for success/failure indicators
                response_buffer = self.receive_until_pattern([
                    "✅", "❌", "Lock opened", "Lock failed", "TIME'S UP", "ALL LOCKS CRACKED"
                ], timeout=10)

                # Check for failure
                if any(fail_marker in response_buffer for fail_marker in [
                    "TIME'S UP", "Lock failed", "❌", "Timeout", "Invalid input"
                ]):
                    logging.error(f"Level {level}: Failed!")
                    clean_response = self.clean_display_text(response_buffer)
                    logging.info(clean_response)
                    return
                else:
                    logging.info(f"Level {level}: Success!")

                # Check for completion after level 4
                if level == 4 or "ALL LOCKS CRACKED" in response_buffer:
                    logging.info("All levels completed!")
                    break

            # Extract and display flag
            final_buffer = self.receive_until_pattern(["flag:", "flag", "KCTF_Jr{"], timeout=5)

            # Combine all received data for flag extraction
            all_data = response_buffer + final_buffer

            flag_patterns = [
                r'(KCTF_Jr\{[^}]+\})',
                r'flag: ([A-Za-z0-9_\-{}]+)',
                r'Here\'s your flag: ([A-Za-z0-9_\-{}]+)',
            ]

            flag_found = False
            for pattern in flag_patterns:
                flag_match = re.search(pattern, all_data, re.IGNORECASE)
                if flag_match:
                    flag = flag_match.group(1)
                    logging.info(f"FLAG FOUND: {flag}")
                    print(f"\n🎉 FLAG: {flag} 🎉")
                    flag_found = True
                    break

            if not flag_found:
                logging.error("Flag not found in expected format!")
                logging.debug(f"Final response: {self.clean_display_text(all_data[-500:])}")

        except Exception as e:
            logging.error(f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.sock:
                self.sock.close()
                logging.info("Connection closed")


if __name__ == "__main__":
    # Command line arguments for host and port
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 10402

    solver = PatternLockSolver(host=host, port=port)
    solver.solve()