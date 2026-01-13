
from pydantic import BaseModel


class Topic(BaseModel):
    topic: str
    urls: list[str]
    sub_topics: list[str]
    content: str
    
    @classmethod
    def from_string(cls, s: str) -> "Topic":
        """
        Parse a string like:
        topic='...' sub_topics=['...'] content='...'
        """
        import ast
        # Convert the string to a dict by wrapping it in dict() syntax
        # topic='x' sub_topics=['y'] content='z' -> dict(topic='x', sub_topics=['y'], content='z')
        dict_str = f"dict({s})"
        try:
            data = eval(dict_str)
            return cls(**data)
        except:
            # Fallback: return with empty fields if parsing fails
            return cls(topic=s, urls=[], sub_topics=[], content="")


class Outline(BaseModel):
    topics: list[Topic]


class ResearchOutput(BaseModel):
    research: str
