FROM python:3.10

RUN apt-get update

RUN mkdir app
WORKDIR app
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD [ "gunicorn", "--workers=5", "--threads=1", "-b 0.0.0.0:8080", "backend.wsgi:app"]