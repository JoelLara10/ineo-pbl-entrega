FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64 \
    SPARK_LOCAL_IP=127.0.0.1 \
    SPARK_TIMEOUT_SECONDS=180 \
    SPARK_JOB_TTL_SECONDS=240 \
    ENABLE_SCHEDULER=false

RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-17-jre-headless \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 10000
CMD ["sh", "-c", "gunicorn --workers 1 --threads 4 --timeout 240 --bind 0.0.0.0:${PORT:-10000} 'app:create_app()'"]
