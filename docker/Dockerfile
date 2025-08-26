# Stage 1: Build the React frontend
FROM node:18-alpine AS node-builder

WORKDIR /app/frontend

COPY src/webapp/frontend/package.json ./
COPY src/webapp/frontend/package-lock.json ./
RUN npm install

COPY src/webapp/frontend/ ./
RUN npm run build

# Stage 2: Build the Python application
FROM python:3.10-slim

WORKDIR /app
RUN mkdir -p /app/reports

# First, copy all files and set up dependencies as root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src /app/src
COPY config /app/config
COPY resources/jira_fields.yml /app/resources/jira_fields.yml
COPY --from=node-builder /app/frontend/build /app/src/webapp/frontend/build
COPY docker/entrypoint.sh /app/entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Now, create a non-root user and switch to it
ARG UID=10001
RUN adduser --disabled-password --gecos "" --home /app --uid ${UID} appuser

# Change ownership of reports directory AFTER user is created
RUN chown appuser:appuser /app/reports

USER appuser

# Expose the port the app runs on
EXPOSE 8000

# Run the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
