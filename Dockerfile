FROM python:3.11-slim

WORKDIR /app

# Copy backend files
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

# Expose port (Railway uses $PORT environment variable)
EXPOSE 8000

# Start command - Railway will set PORT env var
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

