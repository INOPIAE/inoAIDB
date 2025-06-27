import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from app.config import settings


def send_email(to: str, subject: str, body: str):
    message = MIMEMultipart()
    message["Subject"] = subject
    message["From"] = settings.sender_email
    message["To"] = to

    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL(settings.smtp_server, settings.smtp_port) as server:
            server.login(settings.sender_email, settings.smtp_password)
            server.sendmail(settings.sender_email, to, message.as_string())
            print(f"Email sent to {to}")
    except Exception as e:
        print(f"Failed to send email: {e}")
