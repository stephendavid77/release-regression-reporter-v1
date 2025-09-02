Here’s the **full, clean, copy-paste version** of **`gemini.md`**:

---

# **Gemini Python Code Guidelines**

These guidelines ensure **clean, maintainable, and resilient Python code** that follows industry best practices.

---

## **1. Design & Architecture**

* Follow the **SOLID principles** for modular, extensible, and testable design.
* Each **unique feature** should be implemented as a **separate class**.
* Each **distinct functionality** within a feature should be a **separate method**.
* Use **dependency injection** or configuration-driven patterns to reduce coupling.
* Prefer **dataclasses** or **pydantic models** for structured data handling.

---

## **2. Logging & Monitoring**

* Use the **`logging` module**, not `print`, for all logs.
* Include enough context to debug issues easily.
* Logs should:

  * Mark **start and end** of major operations.
  * Include **identifiers** for jobs, users, or transactions when applicable.
  * Use **structured messages** for consistent parsing.

### **Logging Levels**

| Level    | Purpose                                          |
| -------- | ------------------------------------------------ |
| DEBUG    | Detailed information for development.            |
| INFO     | General operational messages.                    |
| WARNING  | Recoverable issues or unusual states.            |
| ERROR    | Non-recoverable issues needing attention.        |
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

## **3. Error Handling & Resilience**

* Use **explicit exception handling** with meaningful error messages.
* Apply **retry strategies** with libraries like `tenacity` for transient failures.
* Use **custom exceptions** for clearer problem diagnosis.
* Fail gracefully and ensure that errors are logged with context.

---

## **4. Containerization with Docker**

* Use a **multi-stage `Dockerfile`** to create optimized and secure container images.
* Build the frontend and backend in separate stages to keep the final image small.
* Use **`docker-compose`** to manage multi-service applications.
* Define clear and consistent naming conventions for services, containers, and networks.

---

## **5. Committing Changes**

* Do not commit any changes unless explicitly instructed to do so by the user.

---

## **Project Overview**

### **Gist of the Application**

The **Release Regression Reporter** is a Python-based application designed to automate the generation of regression reports for software releases.
It integrates with Jira to fetch relevant issue data, processes this data using libraries like `pandas`, and can generate reports in multiple formats (e.g., email, PDF, Excel).
It features:

* A **highly flexible and dynamic JQL construction mechanism** for building Jira queries on the fly.
* **Enhanced email reporting capabilities** to notify specific teams or groups dynamically.

---

### **Tech Stack**

* **Primary Language:** Python
* **Backend Web Framework:** FastAPI (served by Uvicorn)
* **Frontend Web Framework:** React
* **Jira Integration:** `jira` library
* **Data Processing:** `pandas`, `openpyxl`
* **Configuration:** `PyYAML`, `python-dotenv`
* **Templating/Reporting:** `Jinja2`, `premailer`, `md-to-pdf`
* **HTTP Client:** `requests`
* **CLI Framework:** `typer`
* **Logging:** `loguru`
* **Resilience:** `tenacity`
* **HTML/CSS Parsing:** `beautifulsoup4`, `cssutils`, `cssselect`
* **Containerization:** Docker and Docker Compose

---

### **Architecture**

The application follows a **monorepo** structure containing:

* CLI tool
* Web application
* Shared components

---

#### **1. Core Logic / Shared Components (`src/common/sla_reporter`)**

This directory contains:

* **Data retrieval:** `jira_client.py`
* **Processing logic:** `business_logic.py`
* **Report generation:** `report_generator.py`
* **Email notifications:** `email_report.py`
* **Models and configuration:** `models.py`, `config.py`
* **Logging setup:** `logger.py`

**Dynamic JQL Construction:**

* JQL templates and fragments are defined in `regression_config.yaml`.
* Queries are dynamically built using these fragments to support different filters (status, priority, severity, etc.).

**Enhanced Email Reporting:**

* Send reports to a list of emails.
* Notify individual teams based on issues assigned to them.
* Notify predefined groups (e.g., "All APP Teams", Leadership, Regression Team, Tech Leads, Scrum Masters).

---

#### **2. Command-Line Interface (CLI) (`src/cli`)**

* Entry points: `cli_app.py`, `main.py`
* Built with `typer` for commands, arguments, and options.
* Interfaces with `src/common/sla_reporter` for report generation and data fetching.

---

#### **3. Web Application (`src/webapp`)**

* **Backend (`src/webapp/main.py`):**

  * FastAPI app exposing REST endpoints for frontend.
  * Uses core logic from `src/common/sla_reporter`.
  * Provides API endpoints for dynamic filters like Priority and Severity.

* **Frontend (`src/webapp/frontend`):**

  * React SPA that communicates with FastAPI backend.
  * Features multiselect filters and advanced email reporting controls.

---

#### **4. Configuration (`config/`)**

* YAML files for configurations:

  * `config.yaml.sample`
  * `regression_config.yaml.sample`
  * `release-config.yaml.sample`
* Supports:

  * JQL template fragments
  * Team email distribution lists

---

#### **5. Containerization (`docker/`)**

* **Dockerfile:** Defines CLI + backend packaging.
* **docker-compose.yml:** Orchestrates multi-service deployments (backend, frontend, etc.).

---

#### **6. Utilities (`utilities/`)**

* Deployment and dependency scripts.
* Supports Google Cloud, Docker, and local execution workflows.

---

Would you like me to format this as a downloadable `.md` file for convenience?
