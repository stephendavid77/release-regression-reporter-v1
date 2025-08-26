import os
from dotenv import load_dotenv
from src.common.sla_reporter.logger import logger

class Credentials:
    def __init__(self):
        # Determine the path to the .env file relative to the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Assuming .env is in the project root, two levels up from src/common/
        project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
        env_path = os.path.join(project_root, '.env')

        if not os.path.exists(env_path):
            logger.warning(f"Warning: .env file not found at {env_path}")
        load_dotenv(dotenv_path=env_path, override=True)

    def get_jira_credentials(self):
        logger.info("get_jira_credentials method called.")
        jira_email = os.getenv("JIRA_EMAIL")
        jira_api_token = os.getenv("JIRA_API_TOKEN")
        logger.info(f"Retrieved Jira email: {jira_email}")
        logger.info(f"Retrieved Jira API token starting with: {jira_api_token if jira_api_token else 'None'}")

        return jira_email, jira_api_token

    def get_email_credentials(self):
        logger.info("get_email_credentials method called.")
        email_sender_email = os.getenv("EMAIL_SENDER_EMAIL")
        email_sender_password = os.getenv("EMAIL_SENDER_PASSWORD")
        email_smtp_server = os.getenv("EMAIL_SMTP_SERVER")
        email_smtp_port = os.getenv("EMAIL_SMTP_PORT")
        return email_sender_email, email_sender_password, email_smtp_server, email_smtp_port
