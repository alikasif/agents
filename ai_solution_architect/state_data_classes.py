from typing_extensions import TypedDict
from pydantic import BaseModel
from typing import List

class Action(BaseModel):
    action_name: str
    args: str

class ReACTResponse(BaseModel):
    Thought: str
    action_list: List[Action]
    clarifying_questions: List[str]

class DesignReview(BaseModel):
    review_comments: str

class FinalDesign(BaseModel):
    project_short_name: str
    solution_approach: str
    architecure_diagram: str
    design_patterns: str
    llm_sdk_tools_frameworks: str
    detailed_design: str
    prompting_technique: str
    github_links: str

class DeepAgentState(TypedDict):
    input: str
    results: ReACTResponse
    tool_messages: List[str]
    question_answers: List[dict]
    counter: int = 1
    final_design: FinalDesign
    design_review: DesignReview
