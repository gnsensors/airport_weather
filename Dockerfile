# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create directory for logs
RUN mkdir -p /app/logs

# Expose port (Railway will set PORT env variable)
EXPOSE 5000

# Run the application with gunicorn using PORT environment variable
CMD gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 2 --timeout 30 weather_app:app
