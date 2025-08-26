#!/bin/bash

# Ensure the script runs from the project root
cd "$(dirname "$0")/.."

# Wait for Docker to be ready
echo "Verifying Docker connection..."
while ! docker-compose -f docker/docker-compose.yml ps > /dev/null 2>&1; do
    echo "Waiting for Docker to be ready..."
    # Attempt to start Docker if it's not running (macOS)
    if ! docker info > /dev/null 2>&1; then
        echo "Docker is not running. Attempting to start Docker Desktop..."
        open -a Docker
    fi
    sleep 2
done
echo "Docker is ready."

# Double-check connection right before compose
echo "Final Docker check..."
if ! docker version > /dev/null 2>&1; then
    echo "Error: Docker connection lost."
    exit 1
fi

HOST_PORT=8081
echo "Attempting to kill any process on port $HOST_PORT..."

# Find PID using lsof and kill it.
# Using a loop to handle multiple PIDs gracefully.
lsof -t -i:$HOST_PORT | while read -r PID;
do
  if [ -n "$PID" ]; then
    kill -9 "$PID"
    echo "Killed process $PID on port $HOST_PORT."
  fi
done

# If no process was found, lsof returns non-zero, so we print a message.
if ! lsof -t -i:$HOST_PORT > /dev/null; then
    echo "No process found on port $HOST_PORT."
fi


echo "Starting Docker Compose..."
# The -d flag runs containers in the background (detached mode)
docker-compose -f docker/docker-compose.yml up --build -d

echo "Docker containers are starting in the background."
echo "Application should be available at: http://localhost:8081"

# Follow the logs
echo "Following logs... (Press Ctrl+C to stop)"
docker-compose -f docker/docker-compose.yml logs -f
