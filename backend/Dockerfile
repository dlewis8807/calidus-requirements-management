FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for PostgreSQL and compilation
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker caching
COPY requirements.txt ./

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Render will provide $PORT)
EXPOSE 8000

# Run the application (production mode, no --reload)
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
