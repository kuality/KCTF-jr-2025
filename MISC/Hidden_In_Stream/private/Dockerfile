FROM python:3.10-slim-buster

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y socat

ADD hidden_stream_server.py hidden_stream_server.py

EXPOSE 10500

ENTRYPOINT ["python3", "hidden_stream_server.py"]