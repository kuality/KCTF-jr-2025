#!/usr/bin/env python3
"""
Simple solver for Pattern Lock Decoder challenge
"""

import socket
import re
import sys


def lcs_length(s1, s2):
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


def solve(host='localhost', port=10402):
    """Connect and solve the challenge"""

    # Connect to server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    print(f"Connected to {host}:{port}")

    # Buffer for receiving data
    buffer = ""

    try:
        while True:
            # Receive data
            data = sock.recv(4096).decode('utf-8', errors='ignore')
            if not data:
                break

            buffer += data
            print(data, end='', flush=True)  # Print server output

            # Check if we need to send an answer
            if "LCS Length: " in buffer:
                # Extract sequences from buffer
                lines = buffer.split('\n')
                seq1 = None
                seq2 = None

                for i, line in enumerate(lines):
                    if "DNA Sequence 1:" in line:
                        seq1 = line.split("DNA Sequence 1:")[1].strip()
                    elif "DNA Sequence 2:" in line:
                        seq2 = line.split("DNA Sequence 2:")[1].strip()

                if seq1 and seq2:
                    # Calculate LCS
                    answer = lcs_length(seq1, seq2)
                    print(f"{answer}")  # Show what we're sending

                    # Send answer
                    sock.send(f"{answer}\n".encode())

                    # Clear buffer after sending
                    buffer = ""

            # Check for completion
            if "ALL LOCKS CRACKED" in data:
                # Look for flag
                flag_match = re.search(r'(KCTF_Jr\{[^}]+\})', data)
                if flag_match:
                    print(f"\nFLAG: {flag_match.group(1)}")
                break

            # Check for failure
            if any(err in data for err in ["TIME'S UP", "Lock failed", "Invalid input"]):
                print("\nChallenge failed!")
                break

    except Exception as e:
        print(f"\nError: {e}")
    finally:
        sock.close()


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 10402

    solve(host, port)