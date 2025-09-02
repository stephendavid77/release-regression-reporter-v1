# Release Regression Reporter

This tool generates SLA reports for regressions and post-release metrics for specified releases. It integrates with Jira to fetch relevant issue data, processes this data using libraries like `pandas`, and can generate reports in various formats (e.g., email, PDF, Excel). It offers both a command-line interface (CLI) and a web-based user interface.

The application now uses a **dynamic JQL construction mechanism** to build flexible Jira queries based on user selections and predefined report configurations, eliminating the need for separate JQL templates for each report flavor.

---

## Tech Stack

- **Primary Language:** Python
- **Backend Web Framework:** FastAPI (served by Uvicorn)
- **Frontend Web Framework:** React
- **Jira Integration:** `jira` library
- **Data Processing:** `pandas`, `openpyxl`
- **Configuration:** `PyYAML`, `python-dotenv`
- **Templating/Reporting:** `Jinja2`, `premailer`, `md-to-pdf`
- **HTTP Client:** `requests`
- **CLI Framework:** `typer`
- **Logging:** `loguru`
- **Resilience:** `tenacity`
- **HTML/CSS Parsing:** `beautifulsoup4`, `cssutils`, `cssselect`
- **Containerization:** Docker and Docker Compose

---

## Architecture

The application follows a **monorepo** structure, containing both a CLI and a web application, along with shared components.

### 1. Core Logic / Shared Components (`src/common/sla_reporter`)

This directory houses the central business logic for fetching data from Jira (`jira_client.py`), processing it (`business_logic.py`), generating reports (`report_generator.py`), and handling email notifications (`email_report.py`). It also includes data models (`models.py`), configuration (`config.py`), and logging setup (`logger.py`). This module is designed to be reusable by both the CLI and the web application, promoting code reusability and maintaining a single source of truth for core functionalities.

**Dynamic JQL Construction:**  
Instead of hardcoded JQL templates per report, a single `base_jql_template` is defined in `regression_config.yaml`. Specific JQL clauses (for platforms, selling channels, statuses, etc.) are defined as reusable fragments. The `_fetch_report_data` method dynamically combines these fragments based on the selected report's configuration and user-provided filters to build the final JQL query sent to Jira.

### 2. Command-Line Interface (CLI) (`src/cli`)

The CLI, with entry points in `cli_app.py` and `main.py`, allows users to interact with the application directly from the terminal. It uses the `typer` library and imports functionalities from `src/common/sla_reporter`.

### 3. Web Application (`src/webapp`)

- **Backend:** FastAPI app (`src/webapp/main.py`) providing API endpoints and serving frontend static files. It includes endpoints to fetch priorities and severities dynamically.
- **Frontend:** React SPA (`src/webapp/frontend`) that interacts with the FastAPI backend. The sidebar includes filters for team, priority, severity, and platform.

### 4. Configuration (`config/`)

Uses YAML files for configuration:
- `config.yaml.sample`
- `regression_config.yaml.sample`
- `release-config.yaml.sample`

`regression_config.yaml.sample` includes:
- `jql_templates`
- report definitions
- email recipient groups
- team email mappings

### 5. Containerization (`docker/`)

- **`Dockerfile`** defines the Python application image.
- **`docker-compose.yml`** orchestrates backend and optional frontend services.

### 6. Utilities (`utilities/`)

Scripts for dependency management, running locally, or deploying to Google Cloud Run.

---

## Features

- **Standalone CLI** to generate reports
- **Web Application** with user-friendly interface
- **Docker Support** for consistent setup
- **Dynamic JQL Construction** for flexible Jira queries
- **Advanced Filtering**
  - Filter by Team
  - Filter by Jira Status (multiselect)
  - Filter by Priority (multiselect)
  - Filter by Severity (multiselect)
  - Filter by Platform (e.g., iOS, Android)
- **Enhanced Email Reporting**
  - Send to specific recipients or distribution lists
  - Per-team email notifications
  - Predefined groups like Leadership, Regression Team, Tech Leads, Scrum Masters, or All APP Teams
- **Collapsible Report Sections** for easier navigation
- **Modular Architecture**
  - Separated HTML, CSS, and logic
  - Global stylesheet for consistency
  - Jinja2 templating for flexible report layouts

---

## Quick Start with Docker

```bash
# Clone the repository
git clone <repository_url>
cd release-regression-reporter

# Copy sample configs
cp config/config.yaml.sample config/config.yaml
cp config/regression_config.yaml.sample config/regression_config.yaml

# Build and start the app
docker-compose up --build

Setup (Without Docker)
Clone the repository
git clone <repository_url>
cd release-regression-reporter
Install dependencies
pip install -r requirements.txt
cd src/webapp/frontend
npm install && npm run build
Configure the app
Copy and update config/config.yaml
Copy and update config/regression_config.yaml
Define JQL templates, reports, email recipients, and team mappings
Set Jira Personal Access Token (PAT)
Option 1 (less secure): Add api_token directly in config.yaml
Option 2 (secure): Use keyring
python -c "import keyring; keyring.set_password('StandupBot', 'your-email@example.com', 'YOUR_JIRA_PAT')"
Configure Email (Optional)
Update email_settings in config/config.yaml
Or set environment variables:
EMAIL_SENDER_EMAIL
EMAIL_SENDER_PASSWORD
EMAIL_SMTP_SERVER
EMAIL_SMTP_PORT
Usage
Standalone CLI
Run default report:
python -m src.main
With custom config/output:
python -m src.main --config path/to/regression_config.yaml --output path/to/report.html
Web Application (No Docker)
Run locally:
./utilities/run-webapp-no-docker.sh
Open: http://localhost:8000
Web Application (With Docker)
Run:
./run-docker.sh
Open: http://localhost:8000
Deploying to Google Cloud Run
Copy and edit .env
cp .env.sample .env
Add credentials and project details.
Deploy:
./deploy-gcloud.sh
Troubleshooting
Platform Mismatch Warning
If you see:
WARNING: The requested image's platform (linux/amd64) does not match the detected host platform (linux/arm64/v8)
This is safe to ignore on Apple Silicon Macs.
Port Conflict
If you see:
Bind for 0.0.0.0:8000 failed: port is already allocated
Option 1: Kill the process
lsof -i :8000
kill -9 <PID>
Option 2: Use a different port
docker run -p 8081:8000 <image_name>
Then open: http://localhost:8081
Project Structure
config/                # Configuration files
reports/               # Generated reports
src/
  cli/                 # CLI entry points
  common/sla_reporter/ # Core business logic
  webapp/              # Web app backend (FastAPI) and frontend (React)
utilities/             # Helper scripts for local runs and deployments
resources/             # Static resources (e.g., jira_fields.yml)
requirements.txt       # Python dependencies
Dockerfile             # Docker build definition
docker-compose.yml     # Docker orchestration
run-docker.sh          # Script to run app in Docker
deploy-gcloud.sh       # Script to deploy to Cloud Run
License
MIT or project-specific license (update as needed).
