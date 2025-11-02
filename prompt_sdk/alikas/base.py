from typing import List, Optional

class PromptBuilder:
    """
    Base class for structured prompt building.
    Enforces required fields and provides chainable setters.
    """
    REQUIRED_FIELDS = ["task", "context", "examples", "persona", "format", "tone"]

    def __init__(self):
        self.task: Optional[str] = None
        self.context: Optional[str] = None
        self.examples: List[str] = []
        self.persona: Optional[str] = "You are an AI assistant."
        self.format: Optional[str] = None
        self.tone: Optional[str] = "neutral"
        self.instructions: List[str] = []

    def set_task(self, task: str) -> "PromptBuilder":
        self.task = task
        return self

    def set_context(self, context: str) -> "PromptBuilder":
        self.context = context
        return self

    def add_example(self, example: str) -> "PromptBuilder":
        self.examples.append(example)
        return self

    def set_persona(self, persona: str) -> "PromptBuilder":
        self.persona = persona
        return self

    def set_format(self, format_desc: str) -> "PromptBuilder":
        self.format = format_desc
        return self

    def set_tone(self, tone: str) -> "PromptBuilder":
        self.tone = tone
        return self

    def add_instruction(self, instruction: str) -> "PromptBuilder":
        self.instructions.append(instruction)
        return self

    def _validate(self):
        missing = []
        for field in self.REQUIRED_FIELDS:
            val = getattr(self, field)
            if field == "examples" and not val:
                missing.append(field)
            elif field != "examples" and not val:
                missing.append(field)
        if missing:
            raise ValueError(
                f"Prompt validation failed. Missing required fields: {', '.join(missing)}"
            )

    def _base_header(self) -> str:
        self._validate()
        parts = []
        if self.persona:
            parts.append(f"{self.persona}\n")
        if self.task:
            parts.append(f"Task: {self.task}\n")
        if self.context:
            parts.append(f"Context: {self.context}\n")
        if self.tone:
            parts.append(f"Tone: {self.tone}\n")
        if self.format:
            parts.append(f"Output Format: {self.format}\n")
        if self.instructions:
            parts.append("Instructions:\n" + "\n".join(f"- {i}" for i in self.instructions) + "\n")
        if self.examples:
            parts.append("Examples:\n" + "\n".join(self.examples) + "\n")
        return "\n".join(parts)

    def build(self) -> str:
        raise NotImplementedError("Subclasses must implement build().")
