from typing import List, Dict, Optional


# -------------------------
# Base Prompt (with validation)
# -------------------------
class PromptBuilder:
    REQUIRED_FIELDS = ["task", "context", "examples", "persona", "format", "tone"]

    def __init__(self):
        # shared attributes
        self.task: Optional[str] = None
        self.context: Optional[str] = None
        self.examples: List[str] = []
        self.persona: Optional[str] = "You are an AI assistant."
        self.format: Optional[str] = None
        self.tone: Optional[str] = "neutral"
        self.instructions: List[str] = []

    # --- Setters ---
    def set_task(self, task: str): self.task = task; return self
    def set_context(self, context: str): self.context = context; return self
    def add_example(self, example: str): self.examples.append(example); return self
    def set_persona(self, persona: str): self.persona = persona; return self
    def set_format(self, format_desc: str): self.format = format_desc; return self
    def set_tone(self, tone: str): self.tone = tone; return self
    def add_instruction(self, instruction: str): self.instructions.append(instruction); return self

    # --- Validation ---
    def _validate(self):
        missing = []
        for field in self.REQUIRED_FIELDS:
            val = getattr(self, field)
            if field == "examples" and not val:  # must have at least one example
                missing.append(field)
            elif field != "examples" and not val:
                missing.append(field)
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

    # --- Shared assembly ---
    def _base_header(self) -> str:
        self._validate()
        parts = []
        if self.persona: parts.append(f"{self.persona}\n")
        if self.task: parts.append(f"Task: {self.task}\n")
        if self.context: parts.append(f"Context: {self.context}\n")
        if self.tone: parts.append(f"Tone: {self.tone}\n")
        if self.format: parts.append(f"Output Format: {self.format}\n")
        if self.instructions: parts.append("Instructions:\n" + "\n".join(f"- {i}" for i in self.instructions) + "\n")
        if self.examples: parts.append("Examples:\n" + "\n".join(self.examples) + "\n")
        return "\n".join(parts)

    def build(self) -> str:
        raise NotImplementedError("Subclasses must implement build()")


# -------------------------
# Chain of Thought Prompt
# -------------------------
class ChainOfThoughtPrompt(PromptBuilder):
    def __init__(self):
        super().__init__()
        self.thinking_style = "step by step"

    def set_thinking_style(self, style: str):
        self.thinking_style = style
        return self

    def build(self) -> str:
        prompt = self._base_header()
        prompt += f"\nWhen solving, think {self.thinking_style} before giving the final answer.\n"
        prompt += "User Question: {{input}}\n"
        return prompt


# -------------------------
# Tree of Thought Prompt
# -------------------------
class TreeOfThoughtPrompt(PromptBuilder):
    def __init__(self):
        super().__init__()
        self.branching_strategy = "breadth-first"
        self.evaluation_criteria: List[str] = []

    def set_branching_strategy(self, strategy: str):
        self.branching_strategy = strategy
        return self

    def add_evaluation_criteria(self, criterion: str):
        self.evaluation_criteria.append(criterion)
        return self

    def build(self) -> str:
        prompt = self._base_header()
        prompt += f"\nReasoning Strategy: {self.branching_strategy} Tree-of-Thought.\n"
        prompt += "Steps:\n1. Generate multiple reasoning paths.\n2. Evaluate them.\n3. Pick the best path.\n"
        if self.evaluation_criteria:
            prompt += "Evaluation Criteria:\n" + "\n".join(f"- {c}" for c in self.evaluation_criteria) + "\n"
        prompt += "\nUser Question: {{input}}\n"
        return prompt


# -------------------------
# ReAct Prompt
# -------------------------
class ReActPrompt(PromptBuilder):
    def __init__(self):
        super().__init__()
        self.tools: Dict[str, str] = {}
        self.max_actions: int = 5

    def add_tool(self, name: str, description: str):
        self.tools[name] = description
        return self

    def set_max_actions(self, n: int):
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


# -------------------------
# Multi-Shot Prompt
# -------------------------
class MultiShotPrompt(PromptBuilder):
    def __init__(self, shots: int = 2):
        super().__init__()
        self.shots = shots
        self.example_style = "Q&A"

    def set_shots(self, shots: int):
        self.shots = shots
        return self

    def set_example_style(self, style: str):
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


# -------------------------
# Factory
# -------------------------
class PromptFactory:
    registry = {
        "chain_of_thought": ChainOfThoughtPrompt,
        "tree_of_thought": TreeOfThoughtPrompt,
        "react": ReActPrompt,
        "multi_shot": MultiShotPrompt,
    }

    @staticmethod
    def create(prompt_type: str, **kwargs) -> PromptBuilder:
        cls = PromptFactory.registry.get(prompt_type.lower())
        if not cls:
            raise ValueError(f"Unknown prompt type: {prompt_type}")
        return cls(**kwargs)
