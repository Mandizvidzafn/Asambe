FROM python:3.10.4-slim

# Set working directory
WORKDIR /app

# Set environment variables to prevent prompts during install
ENV DEBIAN_FRONTEND=noninteractive

# Install MySQL client libraries + build tools for mysqlclient
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    pkg-config \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip 
# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Expose port for Gunicorn
EXPOSE 8000

# Run Gunicorn with 3 workers, bind to 0.0.0.0:8000
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "3", "-b", "0.0.0.0:8000", "app:app"]
