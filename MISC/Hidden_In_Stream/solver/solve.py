#!/usr/bin/env python3
"""
Solver for Hidden In Stream challenge
"""

import socket
import re
import sys
import time

def solve(host='localhost', port=11000):
    """Connect to server and find the hidden flag"""
    
    print(f"[*] Connecting to {host}:{port}")
    
    try:
        # Create socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)  # 30 second timeout
        sock.connect((host, port))
        
        print("[+] Connected!")
        
        # Receive all data
        received_data = b""
        chunk_size = 4096
        
        print("[*] Receiving data stream...")
        start_time = time.time()
        
        while True:
            try:
                chunk = sock.recv(chunk_size)
                if not chunk:
                    break
                    
                received_data += chunk
                
                # Progress indicator
                if len(received_data) % 10000 == 0:
                    print(f"[*] Received {len(received_data)} bytes...", end='\r')
                
                # Check if we've received the completion message
                if b"Stream complete!" in chunk:
                    break
                    
            except socket.timeout:
                print("\n[!] Socket timeout - assuming stream is complete")
                break
        
        elapsed_time = time.time() - start_time
        print(f"\n[+] Received total of {len(received_data)} bytes in {elapsed_time:.2f} seconds")
        
        # Search for flag pattern
        print("[*] Searching for flag...")
        
        # Try to decode as much as possible
        decoded_parts = []
        i = 0
        while i < len(received_data):
            try:
                # Try to decode a chunk
                chunk = received_data[i:i+1000]
                decoded = chunk.decode('utf-8', errors='ignore')
                decoded_parts.append(decoded)
                i += 1000
            except:
                i += 1000
        
        full_text = ''.join(decoded_parts)
        
        # Search for flag pattern
        flag_pattern = r'KCTF_Jr\{[^}]+\}'
        matches = re.findall(flag_pattern, full_text)
        
        if matches:
            print(f"[+] Found flag: {matches[0]}")
            return matches[0]
        else:
            # Try searching in raw bytes
            print("[*] Searching in raw bytes...")
            flag_bytes_pattern = rb'KCTF_Jr\{[^}]+\}'
            raw_matches = re.findall(flag_bytes_pattern, received_data)
            
            if raw_matches:
                flag = raw_matches[0].decode('utf-8')
                print(f"[+] Found flag: {flag}")
                return flag
            else:
                print("[-] Flag not found!")
                
                # Save data for manual inspection
                with open('stream_dump.bin', 'wb') as f:
                    f.write(received_data)
                print("[*] Saved raw data to stream_dump.bin for manual inspection")
                
                # Also save decoded version
                with open('stream_dump.txt', 'w', encoding='utf-8', errors='ignore') as f:
                    f.write(full_text)
                print("[*] Saved decoded data to stream_dump.txt")
                
                return None
        
    except Exception as e:
        print(f"[-] Error: {e}")
        return None
    finally:
        sock.close()

def main():
    """Main function"""
    if len(sys.argv) > 2:
        host = sys.argv[1]
        port = int(sys.argv[2])
    else:
        host = 'localhost'
        port = 11000
    
    print("=== Hidden In Stream Solver ===")
    flag = solve(host, port)
    
    if flag:
        print(f"\n[+] SUCCESS: {flag}")
    else:
        print("\n[-] Failed to find flag")
        print("[*] Try running: grep -a 'KCTF_Jr{' stream_dump.bin")

if __name__ == "__main__":
    main()