from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import os
from src.common.sla_reporter.reporter import Reporter
from src.common.sla_reporter.config import load_release_config, Config
from src.common.sla_reporter.logger import logger

app = FastAPI()

@app.get("/api/debug/env")
def debug_env():
    return JSONResponse(content=dict(os.environ))

class ReportRequest(BaseModel):
    report_type: str
    release_version: str
    selected_team: str = "All"
    selected_statuses: List[str] = []
    selected_platforms: List[str] = []
    send_email_report: bool = False
    email_recipients: List[str] = []
    include_assignees_in_email_report: bool = False
    include_reportees_in_email_report: bool = False
    include_app_leadership: bool = False
    include_regression_team: bool = False
    include_tech_leads: bool = False
    include_scrum_masters: bool = False

@app.get("/api/reports")
def get_reports():
    config = Config("config/regression_config.yaml")
    reports = config.get("reports", [])
    report_names = [report["name"] for report in reports]
    logger.debug(f"Reports returned: {report_names}")
    return {"reports": report_names}

@app.get("/api/teams")
def get_teams():
    config = Config("config/regression_config.yaml")
    epic_to_team_mapping = config.get("epic_to_team_mapping", {})
    teams = sorted(list(set(epic_to_team_mapping.values())))
    logger.debug(f"Teams returned: {teams}")
    return {"teams": teams}

@app.get("/api/releases")
def get_releases():
    releases, _ = load_release_config()
    release_versions = [release["release_version"] for release in releases]
    logger.debug(f"Releases returned: {release_versions}")
    return {"releases": release_versions}

@app.get("/api/report-types")
def get_report_types():
    report_types_data = {
        "report_types": [
            {
                "name": "All Issues",
                "description": "Generates a comprehensive report including all issues."
            },
            {
                "name": "Open Issues",
                "description": "Generates a report for open issues, excluding cancelled and closed ones."
            }
        ]
    }
    logger.debug(f"Report types returned: {report_types_data}")
    return report_types_data

@app.post("/api/generate-report")
def generate_report(request: ReportRequest):
    reporter = Reporter()
    report_type_mapping = {
        "All Issues": "all_issues",
        "Open Issues": "open_issues"
    }
    internal_report_type = report_type_mapping.get(request.report_type, request.report_type) # Fallback to original if not found

    report_html = reporter.run_webapp(
        release_version=request.release_version,
        report_type=internal_report_type,
        selected_team=request.selected_team,
        selected_statuses=request.selected_statuses,
        selected_platforms=request.selected_platforms,
        email_recipients=request.email_recipients if request.send_email_report else [],
        include_assignees_in_email_report=request.include_assignees_in_email_report,
        include_reportees_in_email_report=request.include_reportees_in_email_report,
        include_app_leadership=request.include_app_leadership,
        include_regression_team=request.include_regression_team,
        include_tech_leads=request.include_tech_leads,
        include_scrum_masters=request.include_scrum_masters,
        send_email_report=request.send_email_report
    )
    return {"report": report_html}

@app.get("/api/download-excel/{filename}")
def download_excel_report(filename: str):
    file_path = os.path.join("reports", filename)
    if os.path.exists(file_path):
        return FileResponse(path=file_path, filename=filename, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    return {"error": "File not found"}

@app.get("/manifest.json", include_in_schema=False)
def serve_manifest():
    return FileResponse("src/webapp/frontend/build/manifest.json")

@app.get("/favicon.ico", include_in_schema=False)
def serve_favicon():
    return FileResponse("src/webapp/frontend/build/favicon.ico")

@app.get("/robots.txt", include_in_schema=False)
def serve_robots():
    return FileResponse("src/webapp/frontend/build/robots.txt")

@app.get("/logo192.png", include_in_schema=False)
def serve_logo192():
    return FileResponse("src/webapp/frontend/build/logo192.png")

@app.get("/logo512.png", include_in_schema=False)
def serve_logo512():
    return FileResponse("src/webapp/frontend/build/logo512.png")

@app.get("/interesting_facts.json", include_in_schema=False)
def serve_interesting_facts():
    return FileResponse("src/webapp/frontend/public/interesting_facts.json")

# Mount the React app
app.mount("/static", StaticFiles(directory="src/webapp/frontend/build/static"), name="static")

@app.get("/{catchall:path}")
def serve_react_app(catchall: str):
    return FileResponse("src/webapp/frontend/build/index.html")
