import logging
from urllib.parse import quote_plus
import pandas as pd
from .models import ReportData, ReleaseInfo
from typing import List
from datetime import datetime, timedelta
import pytz
from .jira_client import calculate_business_hours
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

logger = logging.getLogger(__name__)

est_timezone = pytz.timezone('America/New_York')

# Set up Jinja2 environment
current_dir = Path(__file__).parent
templates_dir = current_dir / "templates"
jinja_env = Environment(loader=FileSystemLoader(templates_dir))

BLACK_FONT_REPORT_NAMES = ["MAPP iOS", "MAPP Android", "BAPP iOS"]

def _format_hours_to_h_m(duration):
    if duration is None:
        return "N/A"
    if isinstance(duration, (int, float)):
        total_minutes = int(round(duration * 60))
    elif isinstance(duration, timedelta):
        total_minutes = int(duration.total_seconds() / 60)
    else:
        return "N/A"

    h = total_minutes // 60
    m = total_minutes % 60
    return f"{h} hrs {m} min"

def _format_time_in_each_status(time_in_each_status):
    items = [f"<li>{status}: {_format_hours_to_h_m(hours)}</li>" for status, hours in time_in_each_status.items() if status != 'Done']
    return f"<ul style='margin: 0; padding: 0; list-style-type: none;'>{''.join(items)}</ul>"

def _check_for_non_business_days(start_date, end_date, holidays):
    current_date = start_date.date()
    end_date_only = end_date.date()
    
    while current_date <= end_date_only:
        if current_date.weekday() >= 5 or current_date in holidays:
            return True
        current_date += timedelta(days=1)
    return False

def _generate_report_title(report_type, release_version, days_since_branch_cut, include_day_suffix=True):
    report_type_text = ""
    if report_type == "all_issues":
        report_type_text = "Full Report"
    elif report_type == "open_issues":
        report_type_text = "Open Issues"

    day_suffix = ""
    if include_day_suffix and isinstance(days_since_branch_cut, int) and days_since_branch_cut > 0:
        day_suffix = f" (Day {days_since_branch_cut})"

    return f"{release_version} - Regression - {report_type_text}{day_suffix}"


def generate_release_info_table(release_info: ReleaseInfo, days_since_branch_cut):
    if not release_info:
        return {}

    team_info = release_info.teams[0] if release_info.teams else None
    em = team_info.em if team_info else 'N/A'
    em_email = team_info.em_email if team_info else ''
    sm = team_info.sm if team_info else 'N/A'
    sm_email = team_info.sm_email if team_info else ''

    return {
        "release_version": release_info.release_version,
        "branch_cut_date": release_info.branch_cut_date,
        "days_since_branch_cut": days_since_branch_cut,
        "em": em,
        "em_email": em_email,
        "sm": sm,
        "sm_email": sm_email
    }


def generate_all_issues_report(reports_data: List[ReportData], sla_config, fix_version, jira_server_url, release_info, days_since_branch_cut, holidays):
    release_version = release_info.release_version
    template = jinja_env.get_template("all_issues_report.html")
    
    release_info_table_data = generate_release_info_table(release_info, days_since_branch_cut)

    grouped_reports_data = []
    for report_data in reports_data:
        issues_by_team = {}
        for issue in report_data.issues:
            team = issue.team or "no epic tagged"
            if team not in issues_by_team:
                issues_by_team[team] = []
            issues_by_team[team].append(issue)
        
        # Sort teams by name, but keep "no epic tagged" last
        sorted_teams = sorted(issues_by_team.items(), key=lambda item: (item[0] == "no epic tagged", item[0]))
        
        grouped_reports_data.append({
            "name": report_data.name,
            "jql": report_data.jql,
            "issues_by_team": sorted_teams
        })

    return template.render(
        report_title=_generate_report_title("all_issues", release_version, days_since_branch_cut, include_day_suffix=False),
        release_version=release_version,
        release_info=release_info_table_data,
        reports_data=grouped_reports_data,
        sla_config=sla_config,
        jira_server_url=jira_server_url,
        holidays=holidays,
        _format_hours_to_h_m=_format_hours_to_h_m,
        _check_for_non_business_days=_check_for_non_business_days,
        calculate_business_hours=calculate_business_hours,
        _format_time_in_each_status=_format_time_in_each_status,
        black_font_report_names=BLACK_FONT_REPORT_NAMES,
        include_sla_approaching=True,
        now_est=datetime.now(est_timezone),
        est_timezone=est_timezone
    )


def generate_open_issues_report(reports_data: List[ReportData], sla_config, fix_version, jira_server_url, release_info, days_since_branch_cut, holidays):
    release_version = release_info.release_version
    template = jinja_env.get_template("open_issues_report.html")

    release_info_table_data = generate_release_info_table(release_info, days_since_branch_cut)

    grouped_reports_data = []
    for report_data in reports_data:
        issues_by_team = {}
        for issue in report_data.issues:
            team = issue.team or "no epic tagged"
            if team not in issues_by_team:
                issues_by_team[team] = []
            issues_by_team[team].append(issue)
        
        # Sort teams by name, but keep "no epic tagged" last
        sorted_teams = sorted(issues_by_team.items(), key=lambda item: (item[0] == "no epic tagged", item[0]))
        
        grouped_reports_data.append({
            "name": report_data.name,
            "jql": report_data.jql,
            "issues_by_team": sorted_teams
        })

    return template.render(
        report_title=_generate_report_title("open_issues", release_version, days_since_branch_cut, include_day_suffix=False),
        release_version=release_version,
        release_info=release_info_table_data,
        reports_data=grouped_reports_data,
        sla_config=sla_config,
        jira_server_url=jira_server_url,
        holidays=holidays,
        _format_hours_to_h_m=_format_hours_to_h_m,
        _check_for_non_business_days=_check_for_non_business_days,
        calculate_business_hours=calculate_business_hours,
        _format_time_in_each_status=_format_time_in_each_status,
        black_font_report_names=BLACK_FONT_REPORT_NAMES,
        include_sla_approaching=False,
        now_est=datetime.now(est_timezone),
        est_timezone=est_timezone
    )


def generate_excel_report(reports_data: List[ReportData], excel_path):
    all_issues = []
    all_statuses = set()
    for report_data in reports_data:
        for issue in report_data.issues:
            for status in issue.time_in_each_status.keys():
                all_statuses.add(status)

    for report_data in reports_data:
        for issue in report_data.issues:
            issue_data = {
                'Jira ID': issue.key,
                'Description': issue.summary,
                'Assignee': issue.assignee,
                'Reporter': issue.reporter,
                'Priority': issue.priority,
                'Current Status': issue.status,
                'Actual Time Took (hours)': issue.time_in_status,
                'Rootcause(RCA)': getattr(issue, 'root_cause', 'N/A'),
                'RCA Category': getattr(issue, 'rca_category', 'N/A')
            }
            for status in all_statuses:
                issue_data[f"Time in {status} (hours)"] = issue.time_in_each_status.get(status, 0)
            all_issues.append(issue_data)
    
    df = pd.DataFrame(all_issues)
    excel_full_path = Path("reports") / excel_path
    df.to_excel(excel_full_path, index=False)