FROM python:3.10-slim-buster
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y socat
ADD pattern_server_async.py pattern_server_async.py
EXPOSE 10402
ENTRYPOINT ["python3", "pattern_server_async.py"]