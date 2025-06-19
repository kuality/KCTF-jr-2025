FROM python:3.10-slim-buster
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y socat
ADD maze_server_async.py maze_server_async.py
EXPOSE 10437
ENTRYPOINT ["python3", "maze_server_async.py"]