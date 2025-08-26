# **Gemini Python Code Guidelines**

These guidelines ensure **clean, maintainable, and resilient Python code** that follows industry best practices.

---

## **1. Design & Architecture**
- Follow the **SOLID principles** for modular, extensible, and testable design.  
- Each **unique feature** should be implemented as a **separate class**.  
- Each **distinct functionality** within a feature should be a **separate method**.  
- Use **dependency injection** or configuration-driven patterns to reduce coupling.  
- Prefer **dataclasses** or **pydantic models** for structured data handling.  

---

## **2. Logging & Monitoring**
- Use the **`logging` module**, not `print`, for all logs.  
- Include enough context to debug issues easily.  
- Logs should:
  - Mark **start and end** of major operations.  
  - Include **identifiers** for jobs, users, or transactions when applicable.  
  - Use **structured messages** for consistent parsing.

### **Logging Levels**
| Level   | Purpose |
|----------|-----------------------------------|
| DEBUG    | Detailed information for development. |
| INFO     | General operational messages. |
| WARNING  | Recoverable issues or unusual states. |
| ERROR    | Non-recoverable issues needing attention. |
| CRITICAL | System-wide failures requiring immediate action. |

### **Logging Example**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)

logger = logging.getLogger(__name__)

def process_data(data):
    logger.info("Starting data processing...")
    try:
        if not data:
            raise ValueError("Data input is empty")
        logger.debug(f"Processing {len(data)} items")
        # Processing logic here
        logger.info("Data processing completed successfully.")
    except ValueError as e:
        logger.error(f"Validation failed: {e}")
    except Exception:
        logger.exception("Unexpected error during data processing")
```

---

## **3. Web Application Development**
- Use **FastAPI** for building efficient and scalable backend APIs.
- Use **React** with **Bootstrap** for creating responsive and mobile-friendly user interfaces.
- Follow a **component-based architecture** in React for reusability and maintainability.
- Use **axios** for making API requests from the frontend.
- Implement **asynchronous task processing** for long-running operations using `FastAPI.BackgroundTasks` or a dedicated task queue like Celery.

---

## **4. Containerization with Docker**
- Use a **multi-stage `Dockerfile`** to create optimized and secure container images.
- Build the frontend and backend in separate stages to keep the final image small.
- Use **`docker-compose`** to manage multi-service applications.
- Define clear and consistent naming conventions for services, containers, and networks.

---

## **5. Committing Changes**
- Do not commit any changes unless explicitly instructed to do so by the user.

---

## **Project Overview**

### Gist of the Application

The "Release Regression Reporter" is a Python-based application designed to automate the generation of regression reports for software releases. It integrates with Jira to fetch relevant issue data, processes this data using libraries like `pandas`, and can generate reports in various formats (e.g., email, PDF, Excel). It offers both a command-line interface (CLI) and a web-based user interface. The presence of an `sla_reporter` component suggests it may also track and report on Service Level Agreements related to regressions or releases.

### Tech Stack

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

### Architecture

The application follows a **monorepo** structure, containing both a CLI and a web application, along with shared components.

#### 1. Core Logic / Shared Components (`src/common/sla_reporter`)

This directory houses the central business logic for fetching data from Jira (`jira_client.py`), processing it (`business_logic.py`), generating reports (`report_generator.py`), and handling email notifications (`email_report.py`). It also includes data models (`models.py`), configuration (`config.py`), and logging setup (`logger.py`). This module is designed to be reusable by both the CLI and the web application, promoting code reusability and maintaining a single source of truth for core functionalities.

#### 2. Command-Line Interface (CLI) (`src/cli`)

The CLI, with entry points in `cli_app.py` and `main.py`, allows users to interact with the application directly from the terminal. It utilizes the `typer` library to define commands, arguments, and options, and imports functionalities from `src/common/sla_reporter` to perform tasks like generating reports or fetching data.

#### 3. Web Application (`src/webapp`)

*   **Backend (`src/webapp/main.py`)**: This is the FastAPI application that exposes API endpoints for the frontend. It consumes the core logic from `src/common/sla_reporter` to fulfill requests and can serve the static files of the React frontend.
*   **Frontend (`src/webapp/frontend`)**: A React single-page application (SPA) that provides the user interface. It communicates with the FastAPI backend via RESTful API calls and is built into static assets.

#### 4. Configuration (`config/`)

The application uses YAML files (`config.yaml.sample`, `regression_config.yaml.sample`, `release-config.yaml.sample`) for configuration, parsed by `PyYAML`, allowing for easy customization.

#### 5. Containerization (`docker/`)

*   **`Dockerfile`**: Defines how the Python application (both CLI and backend) is packaged into a Docker image.
*   **`docker-compose.yml`**: Orchestrates multi-service applications, typically defining services for the FastAPI backend and potentially a separate frontend server.

#### 6. Utilities (`utilities/`)

Contains scripts for dependency management and deployment, including Google Cloud and local Docker/non-Docker execution.
