FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py main.py
COPY requirements.txt requirements.txt
COPY pred8tor.log pred8tor.log
CMD ["python", "/app/main.py"]
