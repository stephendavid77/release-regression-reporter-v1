import concurrent.futures
from datetime import datetime, date
from typing import List

from .config import Config, load_release_config, get_release_info
from .jira_client import SlaJiraClient
from .report_generator import (
    generate_all_issues_report,
    generate_open_issues_report,
)
from .models import ReportData, IssueDetails
from .logger import logger


class BusinessLogic:
    def __init__(self, config: Config, main_config: Config, releases, teams):
        self.config = config
        self.main_config = main_config
        self.releases = releases
        self.teams = teams
        self.release_info = None
        self.jira_client = None

    def generate_report_data(self, release_version: str, report_type: str):
        self.release_info = get_release_info(self.releases, self.teams, release_version)

        if not self.release_info:
            error_message = f"Release '{release_version}' not found in release config."
            logger.error(error_message)
            return f"<h1>{error_message}</h1>", None, None

        branch_cut_date_str = self.release_info.branch_cut_date
        days_since_branch_cut = None
        if branch_cut_date_str:
            branch_cut_date = datetime.strptime(branch_cut_date_str, "%Y-%m-%d").date()
            if branch_cut_date > date.today():
                days_since_branch_cut = "Future date, yet to happen"
            else:
                days_since_branch_cut = (date.today() - branch_cut_date).days

        if report_type not in ["all_issues", "open_issues"]:
            raise ValueError(
                f"Unknown report type: '{report_type}'. Available types are 'all_issues' and 'open_issues'."
            )

        holidays_str = self.config.get("us_holidays", [])
        holidays = {datetime.strptime(h, "%Y-%m-%d").date() for h in holidays_str}

        logger.info("Initializing Jira client...")
        self.jira_client = SlaJiraClient(holidays=holidays)
        jira_server_url = self.jira_client.jira_config["server"]

        if report_type == "all_issues":
            reports_data = self._process_all_issues_reports(release_version)
        elif report_type == "open_issues":
            reports_data = self._process_open_issues_reports(release_version)
        
        logger.debug(f"Reports data fetched: {reports_data}")
        
        html_report = self._generate_html_report(reports_data, report_type, jira_server_url, days_since_branch_cut, release_version, holidays)

        return html_report, reports_data, days_since_branch_cut

    def _generate_html_report(
        self,
        reports_data,
        report_type,
        jira_server_url,
        days_since_branch_cut,
        release_version,
        holidays,
    ):
        logger.info("Generating HTML report...")

        if report_type == "all_issues":
            sla_config = self.config.get("sla")
            html_report = generate_all_issues_report(
                reports_data,
                sla_config,
                release_version,
                jira_server_url,
                self.release_info,
                days_since_branch_cut,
                holidays,
            )
        elif report_type == "open_issues":
            sla_config = self.config.get("sla")
            html_report = generate_open_issues_report(
                reports_data,
                sla_config,
                release_version,
                jira_server_url,
                self.release_info,
                days_since_branch_cut,
                holidays,
            )
        else:
            raise ValueError(f"Unknown report type: {report_type}")
        
        logger.debug(f"Generated HTML report (first 500 chars): {html_report[:500]}")
        return html_report

    def _fetch_report_data(self, report_config, release_version) -> ReportData:
        logger.info(f"Fetching issues for report: {report_config['name']}")
        jql = report_config["jql_template"].format(fix_version=release_version)
        logger.debug(f"JQL: {jql}")
        issues = self.jira_client.search_issues(jql)

        issue_details = []
        for issue in issues:
            issue_details.append(
                IssueDetails(
                    key=issue.key,
                    summary=issue.fields.summary,
                    assignee=issue.fields.assignee.displayName if issue.fields.assignee else 'Unassigned',
                    assignee_email=issue.fields.assignee.emailAddress if issue.fields.assignee else '',
                    reporter=issue.fields.reporter.displayName if issue.fields.reporter else 'N/A',
                    reporter_email=issue.fields.reporter.emailAddress if issue.fields.reporter else '',
                    priority=issue.fields.priority.name,
                    status=issue.fields.status.name,
                    time_in_status=self.jira_client.get_time_in_current_status(issue),
                    time_to_assign=self.jira_client.get_time_to_assign(issue),
                    time_in_each_status=self.jira_client.get_time_in_each_status(issue),
                    created=datetime.strptime(issue.fields.created, "%Y-%m-%dT%H:%M:%S.%f%z"),
                    resolution_date=datetime.strptime(issue.fields.resolutiondate, "%Y-%m-%dT%H:%M:%S.%f%z") if issue.fields.resolutiondate else None,
                )
            )

        return ReportData(
            name=report_config["name"],
            jql=jql,
            issues=issue_details,
        )

    def _fetch_post_release_metrics_data(self, report_config, release_version) -> ReportData:
        logger.info(
            f"Fetching issues for post-release metrics report: {report_config['name']}"
        )
        release_date = datetime.now().strftime("%Y-%m-%d")
        jql = report_config["jql_template"].format(
            fix_version=release_version, release_date=release_date
        )
        logger.debug(f"JQL: {jql}")
        issues = self.jira_client.search_issues(jql)

        issue_details = []
        for issue in issues:
            issue_details.append(
                IssueDetails(
                    key=issue.key,
                    summary=issue.fields.summary,
                    assignee=issue.fields.assignee.displayName if issue.fields.assignee else 'Unassigned',
                    assignee_email=issue.fields.assignee.emailAddress if issue.fields.assignee else '',
                    reporter=issue.fields.reporter.displayName if issue.fields.reporter else 'N/A',
                    reporter_email=issue.fields.reporter.emailAddress if issue.fields.reporter else '',
                    priority=issue.fields.priority.name,
                    status=issue.fields.status.name,
                    time_in_status=self.jira_client.get_time_in_current_status(issue),
                    time_to_assign=self.jira_client.get_time_to_assign(issue),
                    time_in_each_status=self.jira_client.get_time_in_each_status(issue),
                    created=datetime.strptime(issue.fields.created, "%Y-%m-%dT%H:%M:%S.%f%z"),
                    resolution_date=datetime.strptime(issue.fields.resolutiondate, "%Y-%m-%dT%H:%M:%S.%f%z") if issue.fields.resolutiondate else None,
                )
            )

        return ReportData(
            name=report_config["name"],
            jql=jql,
            issues=issue_details,
        )

    def _process_all_issues_reports(self, release_version):
        reports_data = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_report = {
                executor.submit(
                    self._fetch_post_release_metrics_data, # Changed from _fetch_report_data
                    report_config,
                    release_version,
                ): report_config
                for report_config in self.config.get("post_release_metrics", []) # Changed from "reports"
            }
            for future in concurrent.futures.as_completed(future_to_report):
                report_config = future_to_report[future]
                try:
                    data = future.result()
                    reports_data.append(data)
                except Exception as exc:
                    logger.error(f"{report_config['name']} generated an exception: {exc}")
        return reports_data

    def _process_open_issues_reports(self, release_version):
        reports_data = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_report = {
                executor.submit(
                    self._fetch_post_release_metrics_data,
                    report_config,
                    release_version,
                ): report_config
                for report_config in self.config.get("post_release_metrics", [])
            }
            for future in concurrent.futures.as_completed(future_to_report):
                report_config = future_to_report[future]
                try:
                    data = future.result()
                    reports_data.append(data)
                except Exception as exc:
                    logger.error(f"{report_config['name']} generated an exception: {exc}")
        return reports_data
