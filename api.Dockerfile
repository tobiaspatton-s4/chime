FROM python:3.7.7-slim-buster
RUN useradd -m appuser
USER appuser

ENV FLASK_APP=/app/src/api.py
ENV PATH="${PATH}:/home/appuser/.local/bin"

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -q -r requirements.txt

COPY . ./


CMD gunicorn --bind 0.0.0.0:$PORT --chdir src wsgi
