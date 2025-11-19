# ----------- Stage 1: Build dependencies -----------
FROM python:3.10-slim AS builder

WORKDIR /app

# Install OS dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ----------- Stage 2: Final image -----------
FROM python:3.10-slim

WORKDIR /app

# Copy installed Python packages
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy project code
COPY . /app

# Expose Django port
EXPOSE 8003

# Environment variable for logging
ENV PYTHONUNBUFFERED=1

# Run Django server (replace with gunicorn in production)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8003"]
