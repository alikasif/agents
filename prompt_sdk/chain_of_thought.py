from .base import PromptBuilder

class ChainOfThoughtPrompt(PromptBuilder):
    """
    Prompt for chain-of-thought reasoning.
    """
    def __init__(self):
        super().__init__()
        self.thinking_style: str = "step by step"

    def set_thinking_style(self, style: str) -> "ChainOfThoughtPrompt":
        self.thinking_style = style
        return self

    def build(self) -> str:
        prompt = self._base_header()
        prompt += f"\nWhen solving, think {self.thinking_style} before giving the final answer.\n"
        prompt += "User Question: {{input}}\n"
        return prompt
