FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y chromium chromium-driver && \
    rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /

RUN pip install -r requirements.txt

WORKDIR /src

COPY ./src /src

CMD ["python", "app.py"]