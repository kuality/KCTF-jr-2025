import socket
import time

HOST = "localhost"
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
        print(recv, end="")

        # 퀴즈 대기 메시지 감지
        if "What is the name of our club?" in buffer:
            quiz_prompt_detected = True

        # 퀴즈 정답 보내는 시점: 프롬프트 등장까지 기다림
        if quiz_prompt_detected and "> " in buffer:
            answer = "KUality\n"
            print(f"{answer.strip()}")
            time.sleep(0.3)  # 서버가 진짜 받기 직전 약간의 지연
            s.sendall(answer.encode())
            buffer = ""
            answered_quiz = True
            continue

        # echo 입력은 퀴즈 전까지만
        if not answered_quiz and "> " in buffer:
            if echo_count < max_echo_before_quiz:
                msg = "hello\n"
                print(f"> {msg.strip()}")
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
                    print(recv, end="")
                    if "[Session closed]" in recv:
                        break
            except (socket.timeout, ConnectionResetError):
                break
            break
