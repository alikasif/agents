from pydantic import BaseModel

class ChatConversation(BaseModel):
    role: str
    content: str