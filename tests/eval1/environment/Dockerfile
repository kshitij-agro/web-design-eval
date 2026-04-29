FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/bin/python3 /usr/local/bin/python

RUN pip install --no-cache-dir --break-system-packages pytest-playwright

RUN playwright install --with-deps chromium

COPY recipe /app/recipe

COPY reference.png /app/reference.png

WORKDIR /app