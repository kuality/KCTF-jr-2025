#!/usr/bin/env python3
import asyncio
import random
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class ProblemServer:
    FLAG = "KCTF_Jr{h1dd3n_1n_th3_str34m_2025}"
    TOTAL_BYTES = 100000  # 10만 바이트

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    async def run(self):
        server = await asyncio.start_server(self.on_connect, host=self.host, port=self.port)
        logging.info(f"Hidden Stream Server started on {self.host}:{self.port}")
        logging.info(f"Total stream size: {self.TOTAL_BYTES} bytes")
        logging.info("Flag will be hidden somewhere in the stream...")
        await server.wait_closed()

    async def on_connect(self, reader, writer):
        peername = writer.get_extra_info('peername')
        logging.info(f"Client connected: {peername}")

        def cleanup(fu):
            try:
                fu.result()
            except Exception as e:
                logging.error(f"Exception in client connection: {e}")
            logging.info(f"Client disconnected: {peername}")

        task = asyncio.create_task(self.handle_client(reader, writer))
        task.add_done_callback(cleanup)

    async def handle_client(self, reader, writer):
        try:
            await self.handle_problem(reader, writer)
        except Exception as e:
            logging.error(f"Error handling client: {e}")
        finally:
            writer.close()
            await writer.wait_closed()

    async def handle_problem(self, reader, writer):
        # 각 연결마다 새로운 플래그 위치 생성
        flag_position = random.randint(20000, 80000)
        logging.debug(f"Flag will be inserted at position {flag_position}")

        # 초기 메시지
        welcome_msg = b"Welcome to Hidden Stream Challenge!\n"
        welcome_msg += b"I will send you 100,000 bytes... Can you find the hidden flag?\n"
        welcome_msg += b"Starting stream...\n\n"
        writer.write(welcome_msg)
        await writer.drain()

        # 랜덤 바이트 스트림 생성 및 전송
        bytes_sent = 0
        flag_bytes = self.FLAG.encode()
        flag_inserted = False

        # 버퍼링을 위한 청크 크기
        chunk_size = 1024
        buffer = bytearray()

        while bytes_sent < self.TOTAL_BYTES:
            # 플래그를 삽입할 위치에 도달했는지 확인
            if not flag_inserted and bytes_sent + len(buffer) >= flag_position:
                # 플래그 위치까지 채우기
                while len(buffer) < flag_position - bytes_sent:
                    buffer.append(self.generate_random_byte())

                # 플래그 삽입
                buffer.extend(flag_bytes)
                flag_inserted = True
                logging.info(f"Flag inserted at position {flag_position}")
            else:
                # 랜덤 바이트 생성
                buffer.append(self.generate_random_byte())

            # 버퍼가 충분히 차면 전송
            if len(buffer) >= chunk_size or bytes_sent + len(buffer) >= self.TOTAL_BYTES:
                writer.write(buffer)
                await writer.drain()
                bytes_sent += len(buffer)
                buffer.clear()

                # 진행 상황 로그 (1만 바이트마다)
                if bytes_sent % 10000 == 0:
                    logging.debug(f"Sent {bytes_sent} bytes")

        # 완료 메시지
        complete_msg = b"\n\n[+] Stream complete! Did you find the flag?\n"
        writer.write(complete_msg)
        await writer.drain()

        logging.info(f"Stream complete! Sent total of {bytes_sent} bytes")

    def generate_random_byte(self):
        """랜덤 바이트 생성"""
        return random.choice([
            random.randint(0x20, 0x7E),  # 출력 가능한 ASCII
            random.randint(0x80, 0xFF),  # 확장 ASCII
            random.choice([0x00, 0x0A, 0x0D, 0x09])  # 특수 문자
        ])


if __name__ == '__main__':
    server = ProblemServer(host='0.0.0.0', port=10500)
    asyncio.run(server.run())