FROM python:3.10-slim

WORKDIR /app

# System deps (ffmpeg + unzip + wget + build-essential + mp4decrypt)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    ca-certificates \
    wget \
    unzip \
    gnupg \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Install Bento4 (mp4decrypt)
RUN wget -q https://github.com/axiomatic-systems/Bento4/releases/download/1.6.0-641/Bento4-SDK-1-6-0-641.x86_64-unknown-linux.tar.gz -O /tmp/bento4.tar.gz \
    && mkdir -p /opt/bento4 \
    && tar -xzf /tmp/bento4.tar.gz -C /opt/bento4 --strip-components=1 \
    && rm /tmp/bento4.tar.gz \
    && ln -s /opt/bento4/bin/mp4decrypt /usr/local/bin/mp4decrypt
# Python deps (with TgCrypto etc.)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . /app

# Non-root user (optional but safer)
RUN adduser --disabled-password --gecos '' botuser && \
    mkdir -p /app/DOWNLOADS /app/SESSIONS && \
    chown -R botuser:botuser /app

USER botuser

# Start the bot
CMD ["python", "main.py"]
