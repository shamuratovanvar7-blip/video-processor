FROM python:3.11-slim

# System dependencies: FFmpeg + libs needed by opencv-python-headless
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# PORT is honored at runtime; defaults to 8000
ENV PORT=8000
ENV PROCESSING_TIMEOUT_MS=900000
ENV CROPS_DIR=/app/crops

EXPOSE 8000
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}"]