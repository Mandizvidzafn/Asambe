FROM python:3.10.4-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Expose port for Gunicorn
EXPOSE 8000

# Run Gunicorn with 3 workers, bind to 0.0.0.0:8000
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "3", "-b", "0.0.0.0:8000", "app:app"]
