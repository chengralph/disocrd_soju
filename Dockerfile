FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN cat requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .

ENTRYPOINT ["python3", "main.py"]