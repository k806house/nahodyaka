FROM python:3.7-slim

WORKDIR /workdir

COPY . /workdir

RUN pip install -r requirements.txt