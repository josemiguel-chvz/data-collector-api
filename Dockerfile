############################################################
# Dockerfile to run a Django-based web application
############################################################
FROM python:3.9-slim

LABEL maintainer='jose.chavezgald'

ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

RUN mkdir -p /app
WORKDIR /app
ADD . /app/

RUN pip install -r requirements.txt --cache-dir /app/__pycache__