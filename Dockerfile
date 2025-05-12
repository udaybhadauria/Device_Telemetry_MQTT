# Use a lightweight Python base image compatible with Raspberry Pi
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies (optional but useful for MQTT CLI testing)
RUN apt-get update && apt-get install -y \
    build-essential \
    mosquitto \
    mosquitto-clients \
    && rm -rf /var/lib/apt/lists/*

# Copy everything into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the Flask port
EXPOSE 9090

# Run the Flask application
CMD ["python", "telemetry_server.py"]
