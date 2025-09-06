from typing import Annotated
from pydantic import BaseModel
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages

class InformationChunk:

    def __init__(self, content: str, start_idx: int, end_idx: int):
        self.content = content
        self.start_idx = start_idx
        self.end_idx = end_idx
        
    def __str__(self):
        return f"InformationChunk({self.start_idx}:{self.end_idx})"


class WrokerAgentResult(BaseModel):
    name: str
    previous_result: str
    current_result: str


class ChainOfAgentState(TypedDict):
    goal: str
    chunks: list[InformationChunk]
    worker_agent_results: list[WrokerAgentResult]
    final_summary: str
