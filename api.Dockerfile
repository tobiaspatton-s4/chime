FROM python:3.7.7-slim-buster

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -q -r requirements.txt

COPY . ./

ENV FLASK_APP=/app/src/api.py

CMD ["flask", "run", "-h", "0.0.0.0", "-p", "5000"]
