import abc

import pydantic


class SendEmailData(pydantic.BaseModel):
    sender: str | None = None
    recipients: set[str]
    subject: str
    body: str


class EmailClient(abc.ABC):
    @abc.abstractmethod
    def send_email(self, data: SendEmailData):
        pass
