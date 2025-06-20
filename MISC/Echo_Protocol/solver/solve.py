import socket
import time
import sys

HOST = "localhost"  # 또는 원격 서버 IP
PORT = 10123

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.settimeout(1.0)

    buffer = ""
    answered_quiz = False
    echo_count = 0
    max_echo_before_quiz = 50
    quiz_prompt_detected = False

    while True:
        try:
            recv = s.recv(1024).decode()
            if not recv:
                break
        except socket.timeout:
            continue
        except ConnectionResetError:
            break

        buffer += recv
        print(recv, end="", flush=True)

        # 퀴즈 대기 메시지 감지
        if "What is the name of our club?" in buffer:
            quiz_prompt_detected = True

        # 퀴즈 정답 보내는 시점: 프롬프트까지 확인 후 전송
        if quiz_prompt_detected and "> " in buffer:
            answer = "KUality\n"
            print(f"{answer.strip()}", flush=True)
            time.sleep(0.3)
            s.sendall(answer.encode())
            buffer = ""
            answered_quiz = True
            continue

        # echo 입력은 퀴즈 전까지만
        if not answered_quiz and "> " in buffer:
            if echo_count < max_echo_before_quiz:
                msg = "hello\n"
                print(f"{msg.strip()}", flush=True)
                s.sendall(msg.encode())
                echo_count += 1
                buffer = ""

        # 퀴즈 정답 후 종료 메시지 감지
        if answered_quiz:
            try:
                while True:
                    recv = s.recv(1024).decode()
                    if not recv:
                        break
                    print(recv, end="", flush=True)
                    if "[Session closed]" in recv:
                        break
            except (socket.timeout, ConnectionResetError):
                break
            break
