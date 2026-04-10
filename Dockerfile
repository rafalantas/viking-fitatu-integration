FROM python:3.11-slim

WORKDIR /app

RUN pip install requests &&     apt-get update && apt-get install -y cron &&     rm -rf /var/lib/apt/lists/*

COPY viking_fitatu_integration.py .
COPY auth.py .
COPY config.py .

RUN echo "0 7 * * * cd /app && python viking_fitatu_integration.py >> /var/log/viking.log 2>&1" | crontab -

CMD ["cron", "-f"]
