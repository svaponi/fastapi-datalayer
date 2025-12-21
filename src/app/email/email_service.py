import fastapi

from app.email.email_client import EmailClient, SendEmailData


def get_email_client(request: fastapi.Request) -> EmailClient:
    return request.app.email_client


class EmailService:
    def __init__(
        self,
        client: EmailClient = fastapi.Depends(get_email_client),
    ) -> None:
        self.client = client

    def send_email(self, data: SendEmailData):
        self.client.send_email(data)
