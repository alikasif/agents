from typing import List
from .base import PromptBuilder

class TreeOfThoughtPrompt(PromptBuilder):
    """
    Prompt for tree-of-thought reasoning.
    """
    def __init__(self):
        super().__init__()
        self.branching_strategy: str = "breadth-first"
        self.evaluation_criteria: List[str] = []

    def set_branching_strategy(self, strategy: str) -> "TreeOfThoughtPrompt":
        self.branching_strategy = strategy
        return self

    def add_evaluation_criteria(self, criterion: str) -> "TreeOfThoughtPrompt":
        self.evaluation_criteria.append(criterion)
        return self

    def build(self) -> str:
        prompt = self._base_header()
        prompt += f"\nReasoning Strategy: {self.branching_strategy} Tree-of-Thought.\n"
        prompt += (
            "Steps:\n"
            "1. Generate multiple reasoning paths.\n"
            "2. Evaluate them.\n"
            "3. Pick the best path.\n"
        )
        if self.evaluation_criteria:
            prompt += "Evaluation Criteria:\n" + "\n".join(f"- {c}" for c in self.evaluation_criteria) + "\n"
        prompt += "\nUser Question: {{input}}\n"
        return prompt
