# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# system deps needed for yt-dlp/aria2/ffmpeg/mp4decrypt (bento4)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    aria2 \
    ca-certificates \
    wget \
    unzip \
    gnupg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install bento4 (mp4decrypt) - use prebuilt package
RUN wget -q https://github.com/axiomatic-systems/Bento4/releases/download/1.6.0-639/Bento4-SDK-1-6-0-639.x86_64-ubuntu.tar.gz -O /tmp/bento4.tar.gz \
    && mkdir -p /opt/bento4 && tar -xzf /tmp/bento4.tar.gz -C /opt/bento4 --strip-components=1 \
    && rm /tmp/bento4.tar.gz \
    && ln -s /opt/bento4/bin/mp4decrypt /usr/local/bin/mp4decrypt || true

# python deps
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# app code
COPY . /app

# create non-root user
RUN adduser --disabled-password --gecos '' botuser && \
    mkdir -p /app/DOWNLOADS && chown -R botuser:botuser /app

USER botuser

CMD ["python", "main.py"]
