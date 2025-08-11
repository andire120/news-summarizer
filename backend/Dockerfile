# Multi-stage build
# Stage 1: Build a minimal Python environment
FROM python:3.10-slim AS builder

WORKDIR /app

# Install dependencies for model loading
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Final image
FROM python:3.10-slim

WORKDIR /app

# Copy dependencies and application code
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY app ./app

# Expose the port FastAPI runs on
EXPOSE 8000

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]