cd /home/pi/viking

# Sprawdź czy Dockerfile istnieje
ls Dockerfile

# Jeśli nie ma - stwórz go
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

RUN pip install requests && \
    apt-get update && apt-get install -y cron && \
    rm -rf /var/lib/apt/lists/*

COPY viking_fitatu_integration.py .
COPY auth.py .
COPY config.py .

RUN echo "0 7 * * * cd /app && python viking_fitatu_integration.py >> /var/log/viking.log 2>&1" | crontab -

CMD ["cron", "-f"]
EOF

# Dodaj wszystko do gita
git add Dockerfile docker-compose.yml auth.py config.py viking_fitatu_integration.py .gitignore .env.example README.md
git status
git commit -m "Add Dockerfile and all required files"
git push
