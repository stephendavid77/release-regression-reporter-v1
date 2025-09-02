import os
from .config import Config, load_release_config, get_release_info
from .jira_client import SlaJiraClient
from .report_generator import (
    generate_all_issues_report,
    generate_open_issues_report,
    generate_excel_report,
)
from .email_report import send_email
from .logger import logger
import concurrent.futures
from datetime import datetime, date, timedelta
from .models import ReportData, IssueDetails
from typing import List
from premailer import Premailer
from pathlib import Path
import re
from ..credentials import Credentials
import pandas as pd


class Reporter:
    def __init__(self, config_path="config/regression_config.yaml", output_path="sla_report.html"):
        self.config = Config(config_path)
        self.output_path = output_path
        self.main_config = Config("config/config.yaml")
        self.releases, self.teams = load_release_config()
        self.release_info = None
        self.jira_client = None
        self.credentials = Credentials()

    def run_cli(self):
        logger.info("Starting SLA report generation for CLI.")
        report_type = self.config.get("report_type", "regression")
        release_version = self.config.get("fix_version")
        html_report, reports_data, days_since_branch_cut = self._generate_report_data(release_version, report_type, "All", [], [])

        with open(self.output_path, "w") as f:
            f.write(html_report)
        logger.info(f"Report saved to {self.output_path}")

        if report_type == "post_release_metrics":
            excel_path = self.output_path.replace(".html", ".xlsx")
            generate_excel_report(reports_data, excel_path)
            attachment_path = excel_path
        else:
            attachment_path = None

        self._send_email_report(
            html_report,
            report_type,
            days_since_branch_cut,
            release_version,
            self.main_config.get("run_settings", {}).get("email_recipient_email"),
            reports_data,
            attachment_path=attachment_path,
        )

        logger.info("SLA report generation complete.")

    def run_webapp(self, release_version: str, report_type: str, selected_team: str, selected_statuses: List[str], selected_priorities: List[str], selected_severities: List[str], selected_platforms: List[str], email_recipients: List[str], include_assignees_in_email_report: bool = False, include_reportees_in_email_report: bool = False, include_app_leadership: bool = False, include_regression_team: bool = False, include_tech_leads: bool = False, include_scrum_masters: bool = False, include_all_app_teams: bool = False, send_per_team_emails: bool = False, send_email_report: bool = False):
        logger.info(f"Starting SLA report generation for webapp for release {release_version}.")
        html_report, reports_data, days_since_branch_cut = self._generate_report_data(release_version, report_type, selected_team, selected_statuses, selected_priorities, selected_severities, selected_platforms)

        if report_type == "open_issues" or report_type == "all_issues":
            excel_filename = "sla_report.xlsx"
            excel_path = Path("reports") / excel_filename
            generate_excel_report(reports_data, excel_filename)
            attachment_path = excel_path
        else:
            attachment_path = None

        if send_email_report and email_recipients:
            if attachment_path:
                self._send_email_report(
                    html_report,
                    report_type,
                    days_since_branch_cut,
                    release_version,
                    email_recipients,
                    reports_data,
                    attachment_path=attachment_path,
                    include_assignees_in_email_report=include_assignees_in_email_report,
                    include_reportees_in_email_report=include_reportees_in_email_report,
                    include_app_leadership=include_app_leadership,
                    include_regression_team=include_regression_team,
                    include_tech_leads=include_tech_leads,
                    include_scrum_masters=include_scrum_masters,
                )
            else:
                self._send_email_report(
                    html_report,
                    report_type,
                    days_since_branch_cut,
                    release_version,
                    email_recipients,
                    reports_data,
                    include_assignees_in_email_report=include_assignees_in_email_report,
                    include_reportees_in_email_report=include_reportees_in_email_report,
                    include_app_leadership=include_app_leadership,
                    include_regression_team=include_regression_team,
                    include_tech_leads=include_tech_leads,
                    include_scrum_masters=include_scrum_masters,
                )

        return html_report

    def _calculate_business_days(self, start_date, end_date, holidays):
        if start_date > end_date:
            return 0
        business_days = 0
        current_date = start_date
        while current_date <= end_date:
            # weekday() returns 0 for Monday and 6 for Sunday
            if current_date.weekday() < 5 and current_date not in holidays:
                business_days += 1
            current_date += timedelta(days=1)
        return business_days

    def _generate_report_data(self, release_version: str, report_type: str, selected_team: str = "All", selected_statuses: List[str] = [], selected_priorities: List[str] = [], selected_severities: List[str] = [], selected_platforms: List[str] = []):
        self.release_info = get_release_info(self.releases, self.teams, release_version)

        if not self.release_info:
            error_message = f"Release '{release_version}' not found in release config."
            logger.error(error_message)
            return f"<h1>{error_message}</h1>", None, None

        branch_cut_date_str = self.release_info.branch_cut_date
        days_since_branch_cut = None
        holidays_str = self.config.get("us_holidays", [])
        holidays = [datetime.strptime(h, "%Y-%m-%d").date() for h in holidays_str]
        if branch_cut_date_str:
            branch_cut_date = datetime.strptime(branch_cut_date_str, "%Y-%m-%d").date()
            if branch_cut_date > date.today():
                days_since_branch_cut = "Future date, yet to happen"
            else:
                days_since_branch_cut = len(pd.bdate_range(start=branch_cut_date, end=date.today(), holidays=holidays, freq='C'))

        if report_type not in ["all_issues", "open_issues"]:
            raise ValueError(
                f"Unknown report type: '{report_type}'. Available types are 'all_issues' and 'open_issues'."
            )

        logger.info("Initializing Jira client...")
        self.jira_client = SlaJiraClient(credentials=self.credentials, holidays=set(holidays))
        jira_server_url = self.jira_client.jira_config["server"]

        reports_config = self.config.get("reports", [])

        if selected_platforms and "All" not in selected_platforms:
            reports_config = [report for report in reports_config if report["name"] in selected_platforms]

        if report_type == "all_issues":
            reports_data = self._process_all_issues_reports(reports_config, release_version, selected_statuses)
        elif report_type == "open_issues":
            reports_data = self._process_open_issues_reports(reports_config, release_version, selected_statuses)

        if selected_team != "All":
            for report_data in reports_data:
                report_data.issues = [issue for issue in report_data.issues if issue.team == selected_team]
        
        logger.debug(f"Reports data fetched: {reports_data}")
        
        html_report = self._generate_report(reports_data, report_type, jira_server_url, days_since_branch_cut, release_version, holidays)

        return html_report, reports_data, days_since_branch_cut

    def _generate_report(
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

    def _fetch_report_data(self, report_config, release_version, selected_statuses: List[str] = [], selected_priorities: List[str] = [], selected_severities: List[str] = []) -> ReportData:
        logger.info(f"Fetching issues for report: {report_config['name']}")
        project = self.config.get("project") # Get project from config
        jql_templates = self.config.get("jql_templates")

        base_jql = jql_templates["base_jql_template"].format(fix_version=release_version, project=project)
        
        # Build dynamic JQL based on report_config parameters
        final_jql = base_jql

        # Add platform/selling channel clause
        platform_selling_channel_key = report_config.get("platform_selling_channel_key")
        if platform_selling_channel_key:
            final_jql += jql_templates["platform_selling_channel_clauses"][platform_selling_channel_key]

        # Add status clause
        status_filter_key = report_config.get("status_filter_key")
        if status_filter_key:
            final_jql += jql_templates["status_clauses"][status_filter_key]

        # Add created date clause for post-release metrics
        if report_config.get("created_date_filter"):
            release_date = datetime.now().strftime("%Y-%m-%d")
            final_jql += jql_templates["created_date_clause"].format(release_date=release_date)

        # Override status clause if specific statuses are selected by the user
        if selected_statuses:
            status_jql = ", ".join([f'"{s}"' for s in selected_statuses])
            new_status_clause = f"status in ({status_jql})"

            # Replace existing status clause or add a new one before ORDER BY
            if re.search(r'status (not in|in) ', final_jql, re.IGNORECASE):
                final_jql = re.sub(r'status (not in|in) \([^)]*\)', new_status_clause, final_jql, flags=re.IGNORECASE)
            else:
                order_by_match = re.search(r' ORDER BY ', final_jql, re.IGNORECASE)
                if order_by_match:
                    order_by_index = order_by_match.start()
                    final_jql = f"{final_jql[:order_by_index]} AND {new_status_clause} {final_jql[order_by_index:]}"
                else:
                    final_jql = f"{final_jql} AND {new_status_clause}"
        else: # If selected_statuses is empty, remove any existing status clause from the base JQL
            final_jql = re.sub(r' AND status (not in|in) \([^)]*\)', '', final_jql, flags=re.IGNORECASE)
            final_jql = re.sub(r'status (not in|in) \([^)]*\) AND ', '', final_jql, flags=re.IGNORECASE)
            final_jql = re.sub(r'status (not in|in) \([^)]*\)', '', final_jql, flags=re.IGNORECASE)

        # Add priority clause if specific priorities are selected by the user
        if selected_priorities:
            priority_jql = ", ".join([f'"{p}"' for p in selected_priorities])
            final_jql += f" AND priority in ({priority_jql})"

        # Add severity clause if specific severities are selected by the user
        if selected_severities:
            severity_jql = ", ".join([f'"{s}"' for s in selected_severities])
            final_jql += f" AND Severity in ({severity_jql})"

        logger.debug(f"Final JQL: {final_jql}")
        issues = self.jira_client.search_issues(final_jql)

        epic_to_team_mapping = {}
        for team_info in self.teams:
            for epic in team_info.get("regression_epics", []):
                epic_to_team_mapping[epic] = team_info["team_name"]

        issue_details = []
        for issue in issues:
            team = "Uncategorized"
            epic_key = getattr(issue.fields, 'customfield_10014', None)
            if not epic_key and hasattr(issue.fields, 'parent'):
                try:
                    parent_issue = self.jira_client.issue(issue.fields.parent.key)
                    epic_key = getattr(parent_issue.fields, 'customfield_10014', None)
                except Exception as e:
                    logger.warning(f"Could not fetch parent issue for {issue.key}: {e}")

            if epic_key and epic_key in epic_to_team_mapping:
                team = epic_to_team_mapping[epic_key]

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
                    team=team,
                )
            )

        return ReportData(
            name=report_config["name"],
            jql=jql,
            issues=issue_details,
        )

    

    def _process_all_issues_reports(self, reports, release_version, selected_statuses: List[str] = []):
        reports_data = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_report = {
                executor.submit(
                    self._fetch_report_data, # Changed from _fetch_report_data
                    report_config,
                    release_version,
                    selected_statuses,
                ): report_config
                for report_config in reports
            }
            for future in concurrent.futures.as_completed(future_to_report):
                report_config = future_to_report[future]
                try:
                    data = future.result()
                    reports_data.append(data)
                except Exception as exc:
                    logger.error(f"{report_config['name']} generated an exception: {exc}")
        return reports_data

    def _process_open_issues_reports(self, reports, release_version, selected_statuses: List[str] = []):
        reports_data = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_report = {
                executor.submit(
                    self._fetch_report_data,
                    report_config,
                    release_version,
                    selected_statuses,
                ): report_config
                for report_config in reports
            }
            for future in concurrent.futures.as_completed(future_to_report):
                report_config = future_to_report[future]
                try:
                    data = future.result()
                    reports_data.append(data)
                except Exception as exc:
                    logger.error(f"{report_config['name']} generated an exception: {exc}")
        return reports_data

    def _send_email_report(
        self,
        html_report,
        report_type,
        days_since_branch_cut,
        release_version,
        recipients: List[str],
        reports_data: List[ReportData],
        attachment_path=None,
        include_assignees_in_email_report: bool = False,
        include_reportees_in_email_report: bool = False,
        include_app_leadership: bool = False,
        include_regression_team: bool = False,
        include_tech_leads: bool = False,
        include_scrum_masters: bool = False,
        include_all_app_teams: bool = False,
        send_per_team_emails: bool = False,
    ):
        run_settings = self.main_config.get("run_settings", {})
        if run_settings.get("send_email_report"):
            logger.info("Sending email report...")

            # Read the CSS content from index.css
            frontend_css_path = Path(__file__).parent.parent.parent / "webapp" / "frontend" / "src" / "index.css"
            css_text = ""
            if frontend_css_path.exists():
                with open(frontend_css_path, "r") as f:
                    css_text = f.read()

            # Remove h1 tag from html_report for email body
            html_report_for_email = re.sub(r'<h1.*?>(.*?)</h1>', '', html_report, flags=re.DOTALL)

            # Inline CSS using Premailer
            p = Premailer(html_report_for_email, css_text=css_text, keep_style_tags=False, remove_classes=False)
            inlined_html_report = p.transform()

            sender_email, sender_password, smtp_server, smtp_port = self.credentials.get_email_credentials()

            logger.info(f"Using sender email: {sender_email}")
            logger.info(f"Using SMTP server: {smtp_server}:{smtp_port}")
            if sender_password:
                logger.info("EMAIL_SENDER_PASSWORD is set.")
            else:
                logger.error("EMAIL_SENDER_PASSWORD is not set.")

            bcc_recipients = []
            if include_assignees_in_email_report:
                assignee_emails = set()
                for report_data_item in reports_data:
                    for issue in report_data_item.issues:
                        if issue.assignee_email:
                            assignee_emails.add(issue.assignee_email)
                bcc_recipients.extend(list(assignee_emails))
                logger.info(f"Including assignees in BCC: {list(assignee_emails)}")

            if include_reportees_in_email_report:
                reporter_emails = set()
                for report_data_item in reports_data:
                    for issue in report_data_item.issues:
                        if issue.reporter_email:
                            reporter_emails.add(issue.reporter_email)
                bcc_recipients.extend(list(reporter_emails))
                logger.info(f"Including reportees in BCC: {list(reporter_emails)}")

            # Add new email recipients based on flags
            email_config = self.config.get("email_recipients", {})
            if include_app_leadership and email_config.get("app_leadership"):
                bcc_recipients.extend(email_config["app_leadership"])
                logger.info(f"Including App Leadership in BCC: {email_config['app_leadership']}")
            if include_regression_team and email_config.get("regression_team"):
                bcc_recipients.extend(email_config["regression_team"])
                logger.info(f"Including Regression Team in BCC: {email_config['regression_team']}")
            if include_tech_leads and email_config.get("tech_leads"):
                bcc_recipients.extend(email_config["tech_leads"])
                logger.info(f"Including Tech Leads in BCC: {email_config['tech_leads']}")
            if include_scrum_masters and email_config.get("scrum_masters"):
                bcc_recipients.extend(email_config["scrum_masters"])
                logger.info(f"Including Scrum Masters in BCC: {email_config['scrum_masters']}")
            if include_all_app_teams and email_config.get("all_app_teams"):
                bcc_recipients.extend(email_config["all_app_teams"])
                logger.info(f"Including All APP Teams in BCC: {email_config['all_app_teams']}")

            report_type_text = ""
            if report_type == "all_issues":
                report_type_text = "Full Report"
            elif report_type == "open_issues":
                report_type_text = "Open Issues"

            day_suffix = ""
            if isinstance(days_since_branch_cut, int) and days_since_branch_cut > 0:
                day_suffix = f" (Business Day {days_since_branch_cut})"

            subject = f"{release_version} - Regression - {report_type_text}{day_suffix}"

            if send_per_team_emails:
                logger.info("Sending per-team emails...")
                team_issues = {}
                for report_data_item in reports_data:
                    for issue in report_data_item.issues:
                        if issue.team not in team_issues:
                            team_issues[issue.team] = []
                        team_issues[issue.team].append(issue)
                
                team_email_distros = self.config.get("team_email_distros", {})

                for team, issues_list in team_issues.items():
                    team_recipients = team_email_distros.get(team, [])
                    if not team_recipients:
                        logger.warning(f"No email distribution found for team: {team}. Skipping per-team email.")
                        continue
                    
                    # Generate a mini-report for the team
                    team_report_data = [ReportData(name=f"{team} Issues", jql="", issues=issues_list)]
                    team_html_report = self._generate_report(
                        team_report_data,
                        report_type, # Use the main report_type for template selection
                        jira_server_url,
                        days_since_branch_cut,
                        release_version,
                        holidays,
                    )
                    
                    # Inline CSS for team email
                    p_team = Premailer(team_html_report, css_text=css_text, keep_style_tags=False, remove_classes=False)
                    inlined_team_html_report = p_team.transform()

                    team_subject = f"{release_version} - Regression - {report_type_text} - {team}{day_suffix}"

                    send_email(
                        sender=sender_email,
                        recipients=team_recipients,
                        cc_recipients=None,
                        bcc_recipients=None, # No BCC for per-team emails
                        subject=team_subject,
                        body=inlined_team_html_report,
                        smtp_server=smtp_server,
                        smtp_port=int(smtp_port),
                        smtp_user=sender_email,
                        smtp_password=sender_password,
                        attachment_path=attachment_path, # Attachments might need to be handled carefully for per-team
                    )
                logger.info("Per-team emails sent.")
            else: # Send main email if not sending per-team emails
                send_email(
                    sender=sender_email,
                    recipients=recipients,
                    cc_recipients=None,
                    bcc_recipients=bcc_recipients,
                    subject=subject,
                    body=inlined_html_report,
                    smtp_server=smtp_server,
                    smtp_port=int(smtp_port),
                    smtp_user=sender_email,
                    smtp_password=sender_password,
                    attachment_path=attachment_path,
                )
