# Use official Python runtime as a parent image
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_APP=app.py

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt
COPY requirement.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirement.txt

# Copy the entire application
COPY . .

# Expose the port that Flask runs on
EXPOSE 5500

# Create a non-root user to run the app
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Run the Flask application
CMD ["python", "app.py"]
