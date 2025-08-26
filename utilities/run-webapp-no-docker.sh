#!/bin/bash

# Ensure the script runs from the project root
cd "$(dirname "$0")/.."

echo "Attempting to kill any process on port 8000..."
# Find PID using lsof and kill it
PIDS=$(lsof -t -i:8000)
if [ -n "$PIDS" ]; then
  echo "$PIDS" | xargs kill -9
  echo "Killed process(es) on port 8000."
else
  echo "No process found on port 8000."
fi

echo "Checking for Node.js and npm..."
if ! command -v node &> /dev/null
then
    echo "Node.js is not installed. Please install Node.js (e.g., via nvm: https://github.com/nvm-sh/nvm#installing-and-updating) and try again."
    exit 1
fi

if ! command -v npm &> /dev/null
then
    echo "npm is not installed. Please install npm (it usually comes with Node.js) and try again."
    exit 1
fi
echo "Node.js and npm found."

echo "Starting uvicorn for the webapp..."
# Activate the virtual environment
source .venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
python -m pip install -r requirements.txt

# Install frontend dependencies and build frontend
echo "Installing frontend dependencies..."
(cd src/webapp/frontend && npm install)
echo "Building frontend..."
(cd src/webapp/frontend && npm run build)

uvicorn src.webapp.main:app --host 0.0.0.0 --port 8000 --reload &

echo "Webapp started."