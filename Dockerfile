FROM golang:1-bullseye

ENTRYPOINT ["certbot"]

VOLUME /etc/letsencrypt /var/lib/letsencrypt
WORKDIR /opt/certbot

RUN apt update && apt -y install python3 python3-venv python3-dev && \
    python3 -m venv /opt/certbot/ && \
    /opt/certbot/bin/pip install --upgrade pip && \
    /opt/certbot/bin/pip install certbot certbot-dns-multi && \
    ln -s /opt/certbot/bin/certbot /usr/bin/certbot && \
    rm -rf /var/lib/apt/lists/*
