import socket
import threading
import time
import random
import select

HOST = "0.0.0.0"
PORT = 10123
FLAG = "KCTF_Jr{ech0_y0ur_pati3nc3}"

QUIZ_TRIGGER_COUNT = random.randint(25, 35)


def handle_client(conn, addr):
    conn.sendall(b"\n[ Welcome to the Echo Protocol ]\n")
    time.sleep(0.5)
    conn.sendall(b"Say something, and I will echo it back to you.\n")
    time.sleep(0.5)
    conn.sendall(b"Let's see if you truly belong here...\n\n")
    time.sleep(0.5)

    count = 0

    while True:
        conn.sendall(b"> ")
        data = conn.recv(1024)

        if not data:
            break

        msg = data.decode(errors="ignore").strip()
        count += 1

        # echo 출력
        conn.sendall(f"You said: {msg}\n".encode())

        # 중간중간 줄 섞임 방지용 sleep
        time.sleep(0.05)

        # 퀴즈 시작 조건
        if count == QUIZ_TRIGGER_COUNT:
            time.sleep(1)
            conn.sendall(b"\n...Wait. Before we go on, answer this:\n")
            time.sleep(1)
            conn.sendall(b"What is the name of our club?\n")
            time.sleep(0.5)
            conn.sendall(b"> ")

            # 버퍼 완전 클리어
            conn.setblocking(0)
            while True:
                ready = select.select([conn], [], [], 0.1)[0]
                if not ready:
                    break
                try:
                    _ = conn.recv(1024)
                except:
                    break
            conn.setblocking(1)

            # 입력 받기
            answer = conn.recv(1024).decode(errors="ignore").strip()
            time.sleep(0.3)
            conn.sendall(b"\n")

            if answer.lower() == "kuality":
                conn.sendall(b"Correct. You truly belong here.\n\n")
                time.sleep(1)
                conn.sendall(f"{FLAG}\n\n".encode())
            else:
                conn.sendall(b"Wrong. Maybe next time.\n\n")

            time.sleep(0.5)
            conn.sendall(b"[Session closed]\n")
            time.sleep(0.5)
            break

    conn.close()


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print(f"Listening on port {PORT}...")
        while True:
            conn, addr = server.accept()
            threading.Thread(
                target=handle_client, args=(conn, addr), daemon=True
            ).start()


if __name__ == "__main__":
    main()
