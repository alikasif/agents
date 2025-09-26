
from pydantic import BaseModel


class Topic(BaseModel):
    topic: str
    sub_topics: list[str]        


class Outline(BaseModel):
    topics: list[Topic]


class ResearchOutput(BaseModel):
    research: str
