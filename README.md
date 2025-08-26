# Release Regression Reporter

## Gist of the Application

The "Release Regression Reporter" is a Python-based application designed to automate the generation of regression reports for software releases. It integrates with Jira to fetch relevant issue data, processes this data using libraries like `pandas`, and can generate reports in various formats (e.g., email, PDF, Excel). It offers both a command-line interface (CLI) and a web-based user interface. The presence of an `sla_reporter` component suggests it may also track and report on Service Level Agreements related to regressions or releases.

## Tech Stack

*   **Primary Language:** Python
*   **Backend Web Framework:** FastAPI (served by Uvicorn)
*   **Frontend Web Framework:** React
*   **Jira Integration:** `jira` library
*   **Data Processing:** `pandas`, `openpyxl`
*   **Configuration:** `PyYAML`, `python-dotenv`
*   **Templating/Reporting:** `Jinja2`, `premailer`, `md-to-pdf`
*   **HTTP Client:** `requests`
*   **CLI Framework:** `typer`
*   **Logging:** `loguru`
*   **Resilience:** `tenacity`
*   **HTML/CSS Parsing:** `beautifulsoup4`, `cssutils`, `cssselect`
*   **Containerization:** Docker and Docker Compose

## Architecture

The application follows a **monorepo** structure, containing both a CLI and a web application, along with shared components.

### 1. Core Logic / Shared Components (`src/common/sla_reporter`)

This directory houses the central business logic for fetching data from Jira (`jira_client.py`), processing it (`business_logic.py`), generating reports (`report_generator.py`), and handling email notifications (`email_report.py`). It also includes data models (`models.py`), configuration (`config.py`), and logging setup (`logger.py`). This module is designed to be reusable by both the CLI and the web application, promoting code reusability and maintaining a single source of truth for core functionalities.

### 2. Command-Line Interface (CLI) (`src/cli`)

The CLI, with entry points in `cli_app.py` and `main.py`, allows users to interact with the application directly from the terminal. It utilizes the `typer` library to define commands, arguments, and options, and imports functionalities from `src/common/sla_reporter` to perform tasks like generating reports or fetching data.

### 3. Web Application (`src/webapp`)

*   **Backend (`src/webapp/main.py`)**: This is the FastAPI application that exposes API endpoints for the frontend. It consumes the core logic from `src/common/sla_reporter` to fulfill requests and can serve the static files of the React frontend.
*   **Frontend (`src/webapp/frontend`)**: A React single-page application (SPA) that provides the user interface. It communicates with the FastAPI backend via RESTful API calls and is built into static assets.

### 4. Configuration (`config/`)

The application uses YAML files (`config.yaml.sample`, `regression_config.yaml.sample`, `release-config.yaml.sample`) for configuration, parsed by `PyYAML`, allowing for easy customization.

### 5. Containerization (`docker/`)

*   **`Dockerfile`**: Defines how the Python application (both CLI and backend) is packaged into a Docker image.
*   **`docker-compose.yml`**: Orchestrates multi-service applications, typically defining services for the FastAPI backend and potentially a separate frontend server.

### 6. Utilities (`utilities/`)

Contains scripts for dependency management and deployment, including Google Cloud and local Docker/non-Docker execution.

This tool connects to Jira to generate SLA reports for regressions and post-release metrics in a given release.

## Features

-   **Standalone CLI**: Run as a command-line tool to generate reports.
-   **Web Application**: Run as a web application with a user-friendly interface.
-   **Docker Support**: Run the application in a Docker container.
-   **Modular and Maintainable Architecture**:
    -   **Separated Concerns**: HTML, CSS, and business logic are now distinctly separated for improved maintainability and modularity.
    -   **Jinja2 Templating**: HTML generation is handled by Jinja2 templates, allowing for cleaner and more flexible report layouts.
    -   **Centralized CSS**: All report-specific CSS has been moved to a global stylesheet (`src/webapp/frontend/src/index.css`), enabling consistent theming across the application.


## Quick Start with Docker

This section provides the commands to get the application up and running with Docker.

```bash
# 1. Clone the repository
# git clone <repository_url>
# cd release-regression-reporter

# 2. Create the configuration files
cp config/config.yaml.sample config/config.yaml
cp config/regression_config.yaml.sample config/regression_config.yaml

# 3. Build and run the application with Docker
docker-compose up --build
```

## Setup

1.  **Clone the repository (or download the files).**

2.  **Install dependencies:**
    - Python dependencies: `pip install -r requirements.txt`
    - Frontend dependencies: Navigate to `src/webapp/frontend` and run `npm install` then `npm run build`.

3.  **Configure the application:**
    - Create a `config/config.yaml` file by copying the `config/config.yaml.sample` file.
    - Edit `config/config.yaml` with your Jira server URL, email, and email settings.
    - Create a `config/regression_config.yaml` file by copying the `config/regression_config.yaml.sample` file.
    - Edit `config/regression_config.yaml` to configure the reports, fix version, SLAs, and US holidays.
      -   **`report_type`**: This parameter determines which type of report to generate. It can be set to `regression` (default) or `post_release_metrics`.
      -   **`reports`**: This section configures the regression SLA reports. It's a list of reports, each with a `name` and a `jql_template`.
      -   **`post_release_metrics`**: This section configures the post-release metrics reports. It's a list of reports, each with a `name` and a `jql_template`. These reports include additional columns like 'Root Cause' and 'RCA Category', and an attached Excel sheet.

4.  **Set your Jira Personal Access Token (PAT):**
    - The tool can be configured to use a Jira Personal Access Token (PAT) for authentication. You can provide the token directly in the `config.yaml` file or set it up to be retrieved from your system's keyring for better security.
    -   **Option 1: Hardcode in `config.yaml` (less secure):**
        Add `api_token: "YOUR_JIRA_PAT"` under the `jira` section in your `config.yaml`.
    -   **Option 2: Use keyring (more secure):**
        To securely store your token in the keyring, run the following command. Replace the email and token with your own.
        ```bash
        python -c "import keyring; keyring.set_password('StandupBot', 'your-email@example.com', 'YOUR_JIRA_PAT')"
        ```

5.  **Configure Email Sending (Optional):**
    - To receive email reports, configure the `email_settings` in your `config/config.yaml`.
    - Alternatively, you can set the following environment variables:
        -   `EMAIL_SENDER_EMAIL`: Your email address.
        -   `EMAIL_SENDER_PASSWORD`: Your email password or app-specific password.
        -   `EMAIL_SMTP_SERVER`: Your email provider's SMTP server.
        -   `EMAIL_SMTP_PORT`: The SMTP port (usually 587 for TLS).

## Usage

### Standalone CLI

The primary entry point is `src/cli/main.py`.

To generate a report, set the `report_type` in `config/regression_config.yaml` to either `regression` or `post_release_metrics`, and then run:

```bash
python -m src.main
```

-   **Regression Reports**: These reports focus on SLA adherence for regression defects. The report now accurately displays Engineering Manager (EM) and Scrum Master (SM) details in the 'Points of Contact' section.
-   **Post-Release Metrics Reports**: These reports provide insights into post-release issues, including root cause analysis, and come with an attached Excel sheet containing detailed issue data.

You can also specify the config and output file paths:

```bash
python -m src.main --config path/to/your/regression_config.yaml --output path/to/your/report.html
```

### Web Application (without Docker)

To run the web application locally, use the provided script:

```bash
./utilities/run-webapp-no-docker.sh
```

This script will:
- Attempt to kill any process running on port 8000.
- Check for Node.js and npm installation (required for frontend dependencies).
- Activate the Python virtual environment.
- Install Python dependencies.
- Install frontend dependencies and build the frontend.
-   **UI Layout Improvements**: The gap between the sidebar and the report content has been reduced for a more compact and content-rich display.
- Start the FastAPI backend using `uvicorn`.

## Running with Docker

To run the web application with Docker, use `docker-compose`:

```bash
docker-compose up --build
```

The application will be available at [http://localhost:8000](http://localhost:8000).

### Running with Docker (Simplified)

This is the recommended way to run the application locally with Docker.

**1. Create a `.env` file:**

Copy the `.env.sample` file to a new file named `.env`:
```bash
cp .env.sample .env
```

Now, edit the `.env` file and add your credentials.

**2. Run the application:**

Execute the `run-docker.sh` script. This script will automatically build the Docker image and run the container.

```bash
./run-docker.sh
```

The application will be available at [http://localhost:8000](http://localhost:8000).

## Deploying to Google Cloud Run (Simplified)

This is the recommended way to deploy the application to Google Cloud Run.

**1. Create and configure your `.env` file:**

Copy the `.env.sample` file to a new file named `.env`:
```bash
cp .env.sample .env
```

Now, edit the `.env` file and add your credentials and Google Cloud project details.

**2. Run the deployment script:**

Execute the `deploy-gcloud.sh` script:

```bash
./deploy-gcloud.sh
```

This script will automate the entire deployment process, including building the image, pushing it to Artifact Registry, and deploying it to Cloud Run with the correct environment variables.

## Troubleshooting

### Platform Mismatch Warning

When running the Docker container on an Apple Silicon Mac (M1/M2/M3), you may see the following warning:

```
WARNING: The requested image's platform (linux/amd64) does not match the detected host platform (linux/arm64/v8)
```

This warning can be safely ignored for local development. It appears because the Docker image is built for the `linux/amd64` architecture to be compatible with Google Cloud Run, and Docker is using emulation to run it on your `arm64` machine.

### Port Conflict Error

If you see an error like this:

```
docker: Error response from daemon: ... Bind for 0.0.0.0:8000 failed: port is already allocated
```

It means that port `8000` on your machine is already in use by another application. You have two options to resolve this:

**Option 1: Stop the Conflicting Application**

1.  **Find the process ID (PID) using port 8000:**
    ```bash
lsof -i :8000
```

2.  **Stop the process:**
    ```bash
kill -9 <PID>
```
    (Replace `<PID>` with the actual process ID).

**Option 2: Run the Container on a Different Port**

You can map the container's port `8000` to a different port on your machine, for example, `8081`.

```bash
docker run -p 8081:8000 \
  -v "$(pwd)/config:/app/config" \
  -v "$(pwd)/reports:/app/reports" \
  -e JIRA_EMAIL="$JIRA_EMAIL" \
  -e JIRA_API_TOKEN="$JIRA_API_TOKEN" \
  -e EMAIL_SENDER_EMAIL="$EMAIL_SENDER_EMAIL" \
  -e EMAIL_SENDER_PASSWORD="$EMAIL_SENDER_PASSWORD" \
  -e EMAIL_SMTP_SERVER="$EMAIL_SMTP_SERVER" \
  -e EMAIL_SMTP_PORT="$EMAIL_SMTP_PORT" \
  release-regression-reporter
```

If you use this option, your application will be available at [http://localhost:8081](http://localhost:8081).



## Project Structure

- `config/`: Contains the configuration files.
- `reports/`: Directory for generated reports.
- `src/`: Contains the source code.
  - `main.py`: The entry point for the CLI application.
  - `cli_app.py`: Contains the Click CLI application logic.
  - `common/`: Contains common modules.
  - `sla_reporter/`: Contains the modules for the SLA reporting feature.
  - `webapp/`: Contains the web application.
    - `main.py`: the FastAPI backend.
    - `frontend/`: the React frontend.
- `utilities/`: Contains utility scripts and classes.
  - `run-webapp-docker.sh`: Script to run the web application locally with Docker.
  - `run-webapp-no-docker.sh`: Script to run the web application locally without Docker.
- `resources/`: Contains static resources and configuration files.
  - `jira_fields.yml`: Defines custom Jira fields used by the application.
- `requirements.txt`: Lists all Python dependencies.
- `Dockerfile`: Defines the Docker image for the application.
- `docker-compose.yml`: Defines the Docker services for the application.
- `run-docker.sh`: Script to build and run the Docker container locally.
- `deploy-gcloud.sh`: Script to deploy the application to Google Cloud Run.
