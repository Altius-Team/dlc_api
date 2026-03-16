# Altius_API: web con endpoint /dlc y actualización cada 12h
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Variables de entorno (Supabase) se pasan al ejecutar el contenedor
ENV PORT=5000
EXPOSE 5000

# El scheduler (12h) corre en un thread dentro del proceso; no hace falta cron externo
CMD ["python", "main.py"]
