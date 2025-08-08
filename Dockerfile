# Dockerfile
FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /setup

COPY requirements.txt .
RUN pip install --no-warn-script-location -r requirements.txt

COPY . .