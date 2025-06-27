FROM python:3.10-slim-buster

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y socat
RUN python3 -m pip install pycryptodome

ADD prob.py prob.py
ADD flag flag

CMD socat TCP-L:8080,fork,reuseaddr EXEC:"python3 prob.py"