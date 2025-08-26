#!/bin/sh
set -e

# List the contents of the /app/config directory for debugging
echo "--- Listing contents of /app/config ---"
ls -l /app/config
echo "------------------------------------"

# Execute the uvicorn server.
# We use 'exec' to replace the shell process with the Python process, which is a
# best practice for container entrypoints.
exec python -m uvicorn src.webapp.main:app --host 0.0.0.0 --port "${PORT:-8000}"
