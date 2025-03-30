# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

# Want to help us make this template better? Share your feedback here: https://forms.gle/ybq9Krt8jtBL3iCk7

ARG PYTHON_VERSION=3.11.4
FROM python:${PYTHON_VERSION}-slim AS base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=99
ARG GID=100
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    --gid "${GID}" \
    appuser

RUN apt update
RUN apt install -y git-all sqlite3

RUN rm -rf openwebui-auto-knowledge
RUN git clone https://github.com/Slothologist/openwebui-auto-knowledge.git
RUN cd openwebui-auto-knowledge
RUN pip3 install -r openwebui-auto-knowledge/requirements.txt;

RUN echo "run main script...";
USER appuser
ENTRYPOINT python3 openwebui-auto-knowledge/main.py /config/config.yaml;