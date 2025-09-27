FROM python:3.10-slim

WORKDIR /app

# System deps (ffmpeg + unzip + wget + build-essential)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    ca-certificates \
    wget \
    unzip \
    gnupg \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Install Bento4 (mp4decrypt) from official site
RUN wget -q https://www.bento4.com/downloads/Bento4-SDK-1-6-0-639.x86_64-unknown-linux.tar.gz -O /tmp/bento4.tar.gz \
 && mkdir -p /opt/bento4 \
 && tar -xzf /tmp/bento4.tar.gz -C /opt/bento4 --strip-components=1 \
 && rm /tmp/bento4.tar.gz \
 && ln -s /opt/bento4/bin/mp4decrypt /usr/local/bin/mp4decrypt || true

# Python deps
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . /app

# Non-root user
RUN adduser --disabled-password --gecos '' botuser && \
    mkdir -p /app/DOWNLOADS /app/SESSIONS && \
    chown -R botuser:botuser /app

USER botuser

# Start the bot
CMD ["python", "main.py"]
