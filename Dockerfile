FROM python:3.11-slim

WORKDIR /app

# PhonePe SDK lives on a custom index; pull everything else from PyPI
COPY backend/requirements.txt .
RUN pip install --no-cache-dir \
    --index-url https://phonepe.mycloudrepo.io/public/repositories/phonepe-pg-sdk-python \
    --extra-index-url https://pypi.org/simple \
    -r requirements.txt

COPY backend/ .

# Persistent volume for SQLite – mount /data on Railway
RUN mkdir -p /data

ENV PORT=8000

CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
