FROM python:3-buster

ENV SLACK_BOT_TOKEN $SLACK_BOT_TOKEN
ENV SLACK_SIGNING_SECRET $SLACK_SIGNING_SECRET
ENV GOOGLE_API_KEY $GOOGLE_API_KEY
ENV DEFAULT_LOCATION $DEFAULT_LOCATION
ENV DEFAULT_RADIUS $DEFAULT_RADIUS

RUN pip install slack_bolt requests
RUN apt update; apt install -y vim
RUN curl https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip -o a.zip
RUN unzip a.zip

COPY main.py main.py

CMD bash
