FROM python:3.8

RUN pip install Flask gunicorn flask-bootstrap pandas google-cloud-storage flask-googlemaps firebase_admin google-cloud-pubsub

COPY src/ app/
WORKDIR /app

ENV PORT 8080


CMD gunicorn --bind :$PORT app:app

