from typing import Dict
from .base import PromptBuilder

class ReActPrompt(PromptBuilder):
    """
    Prompt for ReAct (Reason + Act) agent.
    """
    def __init__(self):
        super().__init__()
        self.tools: Dict[str, str] = {}
        self.max_actions: int = 5

    def add_tool(self, name: str, description: str) -> "ReActPrompt":
        self.tools[name] = description
        return self

    def set_max_actions(self, n: int) -> "ReActPrompt":
        self.max_actions = n
        return self

    def build(self) -> str:
        prompt = self._base_header()
        if self.tools:
            prompt += "\nAvailable Tools:\n"
            for name, desc in self.tools.items():
                prompt += f"- {name}: {desc}\n"
        prompt += (
            f"\nRules:\n- Use at most {self.max_actions} actions.\n"
            "Format:\n"
            "Thought: reasoning here\n"
            "Action: tool_name[input]\n"
            "PAUSE\n"
            "Observation: result of the action\n"
            "... (repeat as needed)\n"
            "Final Answer: your answer\n\n"
            "User Question: {{input}}\n"
        )
        return prompt
