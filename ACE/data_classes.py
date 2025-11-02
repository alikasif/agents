from pydantic import BaseModel
from typing import TypedDict


class GeneratorOutput(BaseModel):
    user_input: str
    reasoning_trajectories: list[str]


class HyperParameters(BaseModel):
    temperature: float
    max_tokens: int
    stop_sequences: list[str]
    metric: str


class ReflectorOutput(BaseModel):
    user_input: str
    original_prompt: str
    generated_output: str
    diagnosis: str
    suggestions: str
    rationale: str
    hyper_parameters: HyperParameters
    validation_tests: list[str]


class OptimizerOutput(BaseModel):
    prompt_text: str
    user_input: str
    # variant: str
    # notes: list[str]
    # validate: list[str]
    

class OptimizerState(TypedDict):
    user_input: str
    generator_prompt: str
    generator_output: str
    reflector_json: str
    optimizer_output: OptimizerOutput
    re_generator_output: str
    loop_count: int = 0

class Deltas(BaseModel):
    type: str
    content: str
    provenance: str
    action: str

class AgenticReflectorOutput(BaseModel):
    critique_summary: str
    proposed_deltas: list[Deltas]



