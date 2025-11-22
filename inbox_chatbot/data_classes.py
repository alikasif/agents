
from pydantic import BaseModel

class GmailResponse(BaseModel):
    sender: str
    date: str
    subject: str
    id: str
    message_body: str

class GmailToolResponse(BaseModel):
    emails: list[GmailResponse]

class GmailURLResponse(BaseModel):
    urls: list[str]