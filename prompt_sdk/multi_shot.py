from .base import PromptBuilder

class MultiShotPrompt(PromptBuilder):
    """
    Prompt for multi-shot (few-shot) examples.
    """
    def __init__(self, shots: int = 2):
        super().__init__()
        self.shots: int = shots
        self.example_style: str = "Q&A"

    def set_shots(self, shots: int) -> "MultiShotPrompt":
        self.shots = shots
        return self

    def set_example_style(self, style: str) -> "MultiShotPrompt":
        self.example_style = style
        return self

    def build(self) -> str:
        prompt = self._base_header()
        if self.examples:
            prompt += f"\nHere are {self.shots}-shot {self.example_style} examples:\n"
            for i, ex in enumerate(self.examples[:self.shots], 1):
                prompt += f"Example {i}:\n{ex}\n\n"
        prompt += "Now respond to the following input:\nUser Input: {{input}}\n"
        return prompt
