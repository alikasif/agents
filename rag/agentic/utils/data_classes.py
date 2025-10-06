from typing import List, TypedDict, Dict
from langchain.schema import Document
from pydantic import BaseModel, Field


class SubQuestionState(TypedDict):
    datasource: str
    retreived_docs: List[Document]    
    graded_docs: List[Document]


class RagState(TypedDict):
    query: str
    original_query: str
    retreived_docs: List[Document]    
    graded_docs: List[Document]
    llm_response: str
    question_rewrite_count: int = 0
    selected_datasource: str
    sub_questions_dict: Dict[str, SubQuestionState]
    hallucination_grade: str = "no"
    hallucination_check_count: int = 0
    hyde_retreival = str


class Grade(BaseModel):
    binary_score: str = Field(
        description="Relevance score: 'yes' if relevant, or 'no' if not relevant"
    )


class PlannedQueries(BaseModel):
    sub_questions: List[str] = Field(
        description="List of simpler sub-questions derived from the original complex question"
    )

