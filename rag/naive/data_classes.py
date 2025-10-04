from typing import List, TypedDict
from langchain.schema import Document
from pydantic import BaseModel, Field

class RagState(TypedDict):
    query: str
    retreived_docs: List[Document]    
    graded_docs: List[Document]
    llm_response: str


class Grade(BaseModel):

    binary_score: str = Field(
        description="Relevance score: 'yes' if relevant, or 'no' if not relevant"
    )