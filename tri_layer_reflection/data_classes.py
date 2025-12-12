from pydantic import BaseModel

class GeneratorOutput(BaseModel):
    thought_trace: str
    final_answer: str
    tokens_used: int

class ThoughtIntrospectorOutput(BaseModel):
    cognitive_critique: str

class ReflectionOutput(BaseModel):
    improved_prompt: str
    reason_for_changes: str
