FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/* \
    && git config --global user.name "Injection Recipes Backup" \
    && git config --global user.email "backup@injection-recipes.local" \
    && git config --global --add safe.directory /backup

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY migrations/ migrations/
COPY migrations_data/ migrations_data/

ENV DATABASE_PATH=/data/injection.db
ENV BACKUP_DIR=/backup
VOLUME ["/data", "/backup"]
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
