import os
from jira import JIRA
from datetime import datetime, timezone, timedelta
from .config import Config
from .logger import logger
from ..credentials import Credentials


def calculate_business_hours(start_date, end_date, holidays):
    total_minutes = 0
    current_date = start_date
    while current_date < end_date:
        if (
            current_date.weekday() < 5 and current_date.date() not in holidays
        ):  # Monday to Friday and not a holiday
            total_minutes += 1
        current_date += timedelta(minutes=1)
    return total_minutes / 60


def calculate_business_days(start_date, end_date, holidays):
    business_days = 0
    current_date = start_date.date()
    end_date = end_date.date()
    while current_date <= end_date:
        if (
            current_date.weekday() < 5 and current_date not in holidays
        ):  # Monday to Friday and not a holiday
            business_days += 1
        current_date += timedelta(days=1)
    return business_days


class SlaJiraClient:
    def __init__(self, credentials, holidays=None):
        main_config = Config("config/config.yaml")
        self.jira_config = main_config.get("jira")
        self.credentials = credentials
        self._client = self._connect()
        self.holidays = holidays if holidays is not None else set()

    def _connect(self):
        server = self.jira_config["server"]
        jira_email, api_token = self.credentials.get_jira_credentials()
        logger.info(f"Attempting to connect to Jira with email: {jira_email}")
        logger.info(f"Using Jira API token starting with: {api_token if api_token else 'None'}")
        logger.debug(f"DEBUG: jira_email value: '{jira_email}'")
        logger.debug(f"DEBUG: api_token value: '{api_token}'")

        if not jira_email or not api_token:
            logger.error(f"Jira email or API token is empty. Email: '{jira_email}', Token: '{api_token}'")
            raise ConnectionError(
                "Jira credentials not found in environment variables or config.yaml"
            )

        try:
            jira = JIRA(
                server=server, basic_auth=(jira_email, api_token), max_retries=1
            )
            # Test connection
            jira.myself()
            return jira
        except Exception as e:
            logger.error(f"Original Jira connection error: {e}")
            raise ConnectionError(f"Failed to connect to Jira. See logs for original error.")

    def search_issues(self, jql):
        try:
            return self._client.search_issues(jql, expand="changelog", maxResults=False)
        except Exception as e:
            print(f"Error executing JQL: {jql}\n{e}")
            return []

    def get_time_in_current_status(self, issue):
        changelog = issue.changelog
        last_status_change = None

        # Define closed statuses
        closed_statuses = {"Ready for Release", "Ready for Showcase", "Closed", "Done", "Canceled"}
        current_status_name = issue.fields.status.name

        end_date_for_calculation = datetime.now(timezone.utc)

        # If the issue is in a closed status and has a resolution date, use that as the end date
        if current_status_name in closed_statuses and issue.fields.resolutiondate:
            end_date_for_calculation = datetime.strptime(issue.fields.resolutiondate, "%Y-%m-%dT%H:%M:%S.%f%z")
        else:
            # Original logic to find the last status change for open issues
            for history in reversed(changelog.histories):
                for item in history.items:
                    if item.field == "status":
                        last_status_change = history.created
                        break
                if last_status_change:
                    break

        if last_status_change:
            start_date = datetime.strptime(last_status_change, "%Y-%m-%dT%H:%M:%S.%f%z")
        else:
            # If no status change, calculate from creation date
            start_date = datetime.strptime(
                issue.fields.created, "%Y-%m-%dT%H:%M:%S.%f%z"
            )

        # Add debug logging here
        logger.debug(f"Issue: {issue.key}, Status: {current_status_name}")
        logger.debug(f"  Start Date: {start_date}")
        logger.debug(f"  End Date for Calculation: {end_date_for_calculation}")
        calculated_hours = calculate_business_hours(start_date, end_date_for_calculation, self.holidays)
        logger.debug(f"  Calculated Time in Current Status: {calculated_hours} hours")


        return calculated_hours

    def get_time_to_assign(self, issue):
        created_date = datetime.strptime(issue.fields.created, "%Y-%m-%dT%H:%M:%S.%f%z")

        first_assigned_timestamp = None
        changelog = issue.changelog
        logger.debug(f"Getting time to assign for issue {issue.key}")

        for history in changelog.histories:
            for item in history.items:
                if item.field == "assignee":
                    # Check for transition from unassigned (None or empty string) to assigned
                    from_value = item.fromString if hasattr(item, 'fromString') else None
                    to_value = item.toString if hasattr(item, 'toString') else None
                    logger.debug(f"Assignee change for {issue.key}: from='{from_value}' to='{to_value}'")

                    if (from_value is None or from_value == '') and (to_value is not None and to_value != ''):
                        first_assigned_timestamp = datetime.strptime(
                            history.created, "%Y-%m-%dT%H:%M:%S.%f%z"
                        )
                        logger.debug(f"Found first assignment for {issue.key} at {first_assigned_timestamp}")
                        break # Found the first assignment, break inner loop
            if first_assigned_timestamp:
                break # Found the first assignment, break outer loop

        if first_assigned_timestamp:
            return calculate_business_hours(
                created_date, first_assigned_timestamp, self.holidays
            )
        else:
            # If no transition from unassigned to assigned is found
            # Check if it was assigned at creation and never unassigned
            if getattr(issue.fields, "assignee", None):
                logger.debug(f"Issue {issue.key} was assigned at creation or never unassigned.")
                return 0 # Assigned at creation or never unassigned
            else:
                logger.debug(f"Issue {issue.key} is unassigned and was never assigned.")
                return None # Currently unassigned and was never assigned

    def get_business_days_to_resolve(self, issue):
        if not issue.fields.resolutiondate:
            return None
        created_date = datetime.strptime(issue.fields.created, "%Y-%m-%dT%H:%M:%S.%f%z")
        resolution_date = datetime.strptime(
            issue.fields.resolutiondate, "%Y-%m-%dT%H:%M:%S.%f%z"
        )
        return calculate_business_days(created_date, resolution_date, self.holidays)

    def get_time_in_each_status(self, issue):
        time_in_status = {}
        
        all_status_transitions = []
        for history in issue.changelog.histories:
            history_date = datetime.strptime(history.created, "%Y-%m-%dT%H:%M:%S.%f%z")
            for item in history.items:
                if item.field == "status":
                    all_status_transitions.append((history_date, item.fromString, item.toString))
        
        all_status_transitions.sort(key=lambda x: x[0])

        initial_creation_date = datetime.strptime(issue.fields.created, "%Y-%m-%dT%H:%M:%S.%f%z")

        current_status = issue.fields.status.name # Default to current status
        last_change_timestamp = initial_creation_date # Initialize here

        if all_status_transitions:
            current_status = all_status_transitions[0][1] # The status before the first change

        for transition_time, status_from, status_to in all_status_transitions:
            time_spent = calculate_business_hours(last_change_timestamp, transition_time, self.holidays)
            
            if status_from in time_in_status:
                time_in_status[status_from] += time_spent
            else:
                time_in_status[status_from] = time_spent
            
            current_status = status_to
            last_change_timestamp = transition_time

        now = datetime.now(timezone.utc)
        time_spent_in_final_status = calculate_business_hours(last_change_timestamp, now, self.holidays)
        
        if current_status in time_in_status:
            time_in_status[current_status] += time_spent_in_final_status
        else:
            time_in_status[current_status] = time_spent_in_final_status

        return time_in_status