# syntax=docker/dockerfile:1.7
FROM python:3.13-slim-trixie

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN python -m venv /opt/certbot
ENV PATH="/opt/certbot/bin:${PATH}"

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel && \
    pip install certbot && \
    pip install --only-binary=:all: certbot-dns-multi

WORKDIR /etc/letsencrypt
VOLUME ["/etc/letsencrypt", "/var/lib/letsencrypt", "/var/log/letsencrypt"]

ENTRYPOINT ["certbot"]
