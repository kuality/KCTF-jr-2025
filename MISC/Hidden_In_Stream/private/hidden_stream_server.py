#!/usr/bin/env python3
import asyncio
import random
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

FLAG = os.getenv('FLAG', 'KCTF_Jr{h1dd3n_1n_th3_str34m_0f_byt3s}')
PORT = int(os.getenv('PORT', 7777))
HOST = os.getenv('HOST', '0.0.0.0')

TOTAL_BYTES = 100000  # 10만 바이트
FLAG_POSITION = random.randint(20000, 80000)  # 플래그를 중간 어딘가에 숨김

async def handle_client(reader, writer):
    """클라이언트 연결 처리"""
    client_addr = writer.get_extra_info('peername')
    print(f"[+] New connection from {client_addr}")
    
    try:
        # 초기 메시지
        welcome_msg = b"Welcome to Hidden Stream Challenge!\n"
        welcome_msg += b"I will send you 100,000 bytes... Can you find the hidden flag?\n"
        welcome_msg += b"Starting stream...\n\n"
        writer.write(welcome_msg)
        await writer.drain()
        
        # 랜덤 바이트 스트림 생성 및 전송
        bytes_sent = 0
        flag_bytes = FLAG.encode()
        flag_inserted = False
        
        while bytes_sent < TOTAL_BYTES:
            # 플래그를 삽입할 위치에 도달했는지 확인
            if not flag_inserted and bytes_sent >= FLAG_POSITION:
                # 플래그 전송
                writer.write(flag_bytes)
                await writer.drain()
                bytes_sent += len(flag_bytes)
                flag_inserted = True
                print(f"[*] Flag inserted at position {FLAG_POSITION}")
            else:
                # 랜덤 바이트 생성 및 전송
                # 가독성을 해치기 위해 다양한 문자 사용
                random_byte = random.choice([
                    random.randint(0x20, 0x7E),  # 출력 가능한 ASCII
                    random.randint(0x80, 0xFF),  # 확장 ASCII
                    random.choice([0x00, 0x0A, 0x0D, 0x09])  # 특수 문자
                ])
                
                writer.write(bytes([random_byte]))
                bytes_sent += 1
                
                # 100바이트마다 flush
                if bytes_sent % 100 == 0:
                    await writer.drain()
                    
                # 진행 상황 로그 (1만 바이트마다)
                if bytes_sent % 10000 == 0:
                    print(f"[*] Sent {bytes_sent} bytes to {client_addr}")
        
        # 완료 메시지
        complete_msg = b"\n\n[+] Stream complete! Did you find the flag?\n"
        writer.write(complete_msg)
        await writer.drain()
        
    except asyncio.CancelledError:
        print(f"[-] Connection cancelled from {client_addr}")
    except Exception as e:
        print(f"[-] Error handling client {client_addr}: {e}")
    finally:
        writer.close()
        await writer.wait_closed()
        print(f"[*] Connection closed from {client_addr}")

async def main():
    """메인 서버 루프"""
    server = await asyncio.start_server(
        handle_client,
        HOST,
        PORT
    )
    
    addr = server.sockets[0].getsockname()
    print(f"[+] Hidden Stream Server listening on {addr[0]}:{addr[1]}")
    print(f"[*] Total stream size: {TOTAL_BYTES} bytes")
    print(f"[*] Flag will be hidden somewhere in the stream...")
    
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Server shutting down...")
