from pydantic import BaseModel
from typing import Optional
from enum import Enum

class AnalystOutput(BaseModel):
    thought: str
    action: str
    topics_to_research: list[str]    

class TopicResearch(BaseModel):
    topic: str
    detailed_researched_content: str
    references: list[str]

class ResearcherOutput(BaseModel):
    thought: str
    action: str
    detailed_research: TopicResearch

class EditorOutput(BaseModel):
    thought: str
    action: str
    ordered_topics: list[str]

class GoogleSearchItem:
    title: str
    link: str
    snippet: str

class GoogleSearchResults:
    query: str
    search_results: list[GoogleSearchItem]



class LLMType(Enum):
        OPEN_AI = 1
        GEMINI = 2
        ANTHROPIC = 3
        DEEPSEEK = 4