FROM python:3.10-slim

WORKDIR /app

# requirements पहले copy करें
COPY requirements.txt /app/

# pip install root user से
RUN pip install --no-cache-dir -r requirements.txt

# अब app code copy करें
COPY . /app

# non-root user
RUN adduser --disabled-password --gecos '' botuser && \
    mkdir -p /app/DOWNLOADS && chown -R botuser:botuser /app

USER botuser

CMD ["python", "main.py"]
