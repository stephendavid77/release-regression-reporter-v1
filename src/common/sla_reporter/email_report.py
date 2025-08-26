import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .logger import logger
from email.mime.application import MIMEApplication


def send_email(
    sender,
    recipients,
    subject,
    body,
    smtp_server,
    smtp_port,
    smtp_user,
    smtp_password,
    cc_recipients=None,
    bcc_recipients=None,
    attachment_path=None,
):
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    if cc_recipients:
        msg["Cc"] = ", ".join(cc_recipients)
    if bcc_recipients:
        msg["Bcc"] = ", ".join(bcc_recipients)
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "html"))

    if attachment_path:
        with open(attachment_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
        part["Content-Disposition"] = (
            f'attachment; filename="{os.path.basename(attachment_path)}"'
        )
        msg.attach(part)

    try:
        all_recipients = list(recipients)
        if cc_recipients:
            all_recipients.extend(cc_recipients)
        if bcc_recipients:
            all_recipients.extend(bcc_recipients)
        logger.info(f"Sending email to: {recipients} (CC: {cc_recipients}) (BCC: {bcc_recipients})")
        logger.info(f"Attempting to connect to email server: {smtp_server}:{smtp_port}")
        with smtplib.SMTP(smtp_server, smtp_port) as smtp:
            smtp.starttls()
            smtp.login(smtp_user, smtp_password)
            logger.info("SMTP login successful.")
            failed_recipients = smtp.send_message(msg, sender, all_recipients)
            if failed_recipients:
                logger.error(f"Failed to send email to: {failed_recipients}")
                return False
            else:
                logger.info("Email sent successfully!")
                return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False
