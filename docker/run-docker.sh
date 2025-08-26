#!/bin/bash

# Build the Docker image
# If you are on an Apple Silicon Mac (M1/M2/M3), you may need to use the --platform flag
# docker build --platform linux/amd64 -t release-regression-reporter .
docker build -t release-regression-reporter .

# Stop any existing container using port 8000
docker stop $(docker ps -q --filter "publish=8000")

# Run the Docker container
docker run -p 8000:8000 \
  -v "$(pwd)/config:/app/config" \
  -v "$(pwd)/reports:/app/reports" \
  --env-file .env \
  release-regression-reporter