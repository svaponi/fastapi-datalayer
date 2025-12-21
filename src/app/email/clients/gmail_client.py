import logging
import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText

from app.email.email_client import EmailClient, SendEmailData


class GmailEmailClient(EmailClient):

    def __init__(self, username: str, app_password: str):
        super().__init__()
        self.logger = logging.getLogger(f"{self.__module__}.{type(self).__name__}")
        self.username = username
        self.app_password = app_password
        self.from_ = username if "@" in username else f"{username}@email.com"

    def send_email(self, data: SendEmailData):
        msg = MIMEText(data.body, "html")
        msg["Subject"] = data.subject
        msg["To"] = ", ".join(data.recipients)
        msg["From"] = self.from_
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=5) as smtp_server:
            smtp_server.login(self.username, self.app_password)
            self.logger.info(
                f"Sending email - From: {msg["From"]}, To: {msg["To"]}, Subject: {msg["Subject"]}"
            )
            smtp_server.sendmail(self.from_, list(data.recipients), msg.as_string())


if __name__ == "__main__":
    import dotenv

    dotenv.load_dotenv()
    client = GmailEmailClient(
        os.environ["GMAIL_USERNAME"], os.environ["GMAIL_APP_PASSWORD"]
    )
    client.send_email(
        SendEmailData(
            recipients={"samuel@zymtools.com"},
            subject=f"Test {datetime.now()}",
            body="I am a test email. Delete me!",
        )
    )
