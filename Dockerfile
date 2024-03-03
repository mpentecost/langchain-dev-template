FROM python:3.11-bookworm as build

RUN mkdir /app && mkdir /py_venv
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    gcc

WORKDIR /app
# RUN python -m venv /py_venv
RUN pip install --upgrade virtualenv && virtualenv /py_venv --python=python3.11
ENV PATH="/py_venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
