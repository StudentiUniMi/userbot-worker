FROM python:3.9-slim

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY main.py .

ENTRYPOINT ["python3", "main.py"]