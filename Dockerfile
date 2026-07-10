# Optional container image for the API server.
# Build:  docker build -t chokepoint-research-agent .
# Run:    docker run --rm -p 8000:8000 --env-file .env chokepoint-research-agent

FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Generated reports land here; mount a volume in production if needed
RUN mkdir -p /app/reports

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')" || exit 1

# Pass --host/--port via default callback flags
CMD ["python", "main.py", "--server", "--host", "0.0.0.0", "--port", "8000"]
