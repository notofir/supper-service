FROM python:3-buster

ENV SLACK_BOT_TOKEN _
ENV SLACK_SIGNING_SECRET _
ENV GOOGLE_API_KEY _
ENV DEFAULT_LOCATION _
ENV DEFAULT_RADIUS 1000

RUN pip install slack_bolt requests
RUN apt update; apt install -y vim
RUN curl https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip -o a.zip
RUN unzip a.zip

COPY main.py main.py

CMD bash
