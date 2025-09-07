
from pydantic import BaseModel

class Action(BaseModel):
    tool_name: str
    args: str

class Blogger(BaseModel):    
    content: str
    action: Action