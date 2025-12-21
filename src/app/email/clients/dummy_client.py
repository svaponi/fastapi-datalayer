import logging
import os
import smtplib
from collections import deque
from datetime import datetime
from email.mime.text import MIMEText

from app.email.email_client import EmailClient, SendEmailData


class DummyEmailClient(EmailClient):

    def __init__(self):
        super().__init__()
        self.inbox: deque[SendEmailData] = deque()

    def send_email(self, data: SendEmailData):
        self.inbox.append(data)
