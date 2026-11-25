# Kimyo video-yechim Telegram boti (kod chembot/ papkasida).
# Ildizdan quriladi, shuning uchun Railway'da Root Directory kerak emas.
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg fonts-dejavu-core fonts-liberation && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY chembot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY chembot/ .
CMD ["python", "bot.py"]
