#!/usr/bin/env python3
import asyncio
import random
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

FLAG = os.getenv('FLAG', 'KCTF_Jr{test_flag_hidden_in_stream}')
PORT = int(os.getenv('PORT', 10500))
HOST = os.getenv('HOST', '0.0.0.0')

TOTAL_BYTES = 100000  # 10만 바이트


async def handle_client(reader, writer):
    """클라이언트 연결 처리"""
    client_addr = writer.get_extra_info('peername')
    print(f"[+] New connection from {client_addr}")

    # 각 연결마다 새로운 플래그 위치 생성
    flag_position = random.randint(20000, 80000)

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

        # 버퍼링을 위한 청크 크기
        chunk_size = 1024
        buffer = bytearray()

        while bytes_sent < TOTAL_BYTES:
            # 플래그를 삽입할 위치에 도달했는지 확인
            if not flag_inserted and bytes_sent + len(buffer) >= flag_position:
                # 플래그 위치까지 채우기
                while len(buffer) < flag_position - bytes_sent:
                    random_byte = random.choice([
                        random.randint(0x20, 0x7E),  # 출력 가능한 ASCII
                        random.randint(0x80, 0xFF),  # 확장 ASCII
                        random.choice([0x00, 0x0A, 0x0D, 0x09])  # 특수 문자
                    ])
                    buffer.append(random_byte)

                # 플래그 삽입
                buffer.extend(flag_bytes)
                flag_inserted = True
                print(f"[*] Flag inserted at position {flag_position}")
            else:
                # 랜덤 바이트 생성
                random_byte = random.choice([
                    random.randint(0x20, 0x7E),  # 출력 가능한 ASCII
                    random.randint(0x80, 0xFF),  # 확장 ASCII
                    random.choice([0x00, 0x0A, 0x0D, 0x09])  # 특수 문자
                ])
                buffer.append(random_byte)

            # 버퍼가 충분히 차면 전송
            if len(buffer) >= chunk_size or bytes_sent + len(buffer) >= TOTAL_BYTES:
                try:
                    writer.write(buffer)
                    await writer.drain()
                    bytes_sent += len(buffer)
                    buffer.clear()

                    # 진행 상황 로그 (1만 바이트마다)
                    if bytes_sent % 10000 == 0:
                        print(f"[*] Sent {bytes_sent} bytes to {client_addr}")

                except (ConnectionResetError, BrokenPipeError, asyncio.CancelledError) as e:
                    print(f"[-] Connection lost from {client_addr}: {e}")
                    return

        # 완료 메시지
        complete_msg = b"\n\n[+] Stream complete! Did you find the flag?\n"
        writer.write(complete_msg)
        await writer.drain()

    except (ConnectionResetError, BrokenPipeError) as e:
        print(f"[-] Connection error from {client_addr}: {e}")
    except asyncio.CancelledError:
        print(f"[-] Connection cancelled from {client_addr}")
    except Exception as e:
        print(f"[-] Unexpected error handling client {client_addr}: {e}")
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except:
            pass  # 이미 닫힌 연결 무시
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