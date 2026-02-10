FROM python:3.11-slim

WORKDIR /app

# Copy backend files
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

# Railway will provide PORT environment variable
ENV PORT=8000

# Start command - use shell form to allow env var substitution
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT


