FROM python:3.10-bookworm

RUN apt-get update

RUN mkdir /app
WORKDIR /app

ENV PYTHONPATH /app
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD [ "python3", "bulk-load/bulk_load.py"]