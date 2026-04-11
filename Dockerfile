FROM python:3.11-slim

WORKDIR /app

# Instalează dependențele sistem + supervisor
RUN apt-get update && apt-get install -y --no-install-recommends \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Instalează dependențele Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiază tot codul
COPY . .

# Directorul pentru baza de date (montat ca volum persistent în Fly.io)
RUN mkdir -p /data

EXPOSE 8000

CMD ["supervisord", "-c", "supervisord.conf", "-n"]
