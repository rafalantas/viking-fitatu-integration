FROM python:3.11-slim

WORKDIR /app

RUN pip install requests

COPY viking_fitatu_integration.py .
COPY auth.py .
COPY config.py .

CMD ["tail", "-f", "/dev/null"]
