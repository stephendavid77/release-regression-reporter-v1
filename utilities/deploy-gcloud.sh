#!/bin/bash

# Load environment variables from .env file in the project root
# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
# Navigate up to the project root (assuming script is in docker/)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

if [ -f "$PROJECT_ROOT/.env" ]; then
  set -a
  . "$PROJECT_ROOT/.env"
  set +a
else
  echo "Error: .env file not found at $PROJECT_ROOT/.env"
  exit 1
fi

# Set local image name
LOCAL_IMAGE_NAME="release-regression-reporter"

# Construct the remote image name
REMOTE_IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$LOCAL_IMAGE_NAME:latest"

# 1. Authenticate with GCP
echo "Authenticating with GCP..."
gcloud auth login
gcloud config set project $PROJECT_ID

# 2. Enable required APIs
echo "Enabling required APIs..."
gcloud services enable artifactregistry.googleapis.com
gcloud services enable run.googleapis.com

# 3. Create Artifact Registry (skip if already exists)
echo "Creating Artifact Registry repository..."
gcloud artifacts repositories create $REPO_NAME \
  --repository-format=docker \
  --location=$REGION \
  --description="Docker repository for Python web apps" || echo "Repository already exists, skipping"

# 4. Configure Docker to use Artifact Registry
echo "Configuring Docker..."
gcloud auth configure-docker $REGION-docker.pkg.dev

# 5. Build Docker image for linux/amd64
# Change to project root for docker build context
pushd "$PROJECT_ROOT" > /dev/null

echo "Building Docker image..."
docker buildx build --no-cache --platform linux/amd64 -f docker/Dockerfile -t $LOCAL_IMAGE_NAME .

# Change back to original directory
popd > /dev/null

# 6. Tag and push Docker image
echo "Tagging and pushing Docker image..."
docker tag $LOCAL_IMAGE_NAME $REMOTE_IMAGE
docker push $REMOTE_IMAGE

# 7. Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $REMOTE_IMAGE \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --update-env-vars=JIRA_EMAIL="$JIRA_EMAIL",JIRA_API_TOKEN="$JIRA_API_TOKEN",EMAIL_SENDER_EMAIL="$EMAIL_SENDER_EMAIL",EMAIL_SENDER_PASSWORD="$EMAIL_SENDER_PASSWORD",EMAIL_SMTP_SERVER="$EMAIL_SMTP_SERVER",EMAIL_SMTP_PORT="$EMAIL_SMTP_PORT"

# 8. Done
echo "Deployment complete! Visit the Cloud Run URL printed above."