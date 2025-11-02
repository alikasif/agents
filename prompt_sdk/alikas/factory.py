from typing import Type, Dict
from .chain_of_thought import ChainOfThoughtPrompt
from .tree_of_thought import TreeOfThoughtPrompt
from .react import ReActPrompt
from .multi_shot import MultiShotPrompt

class PromptFactory:
    """
    Factory for creating prompt builders by type.
    """
    registry: Dict[str, Type] = {
        "chain_of_thought": ChainOfThoughtPrompt,
        "tree_of_thought": TreeOfThoughtPrompt,
        "react": ReActPrompt,
        "multi_shot": MultiShotPrompt,
    }

    @staticmethod
    def create(prompt_type: str, **kwargs):
        cls = PromptFactory.registry.get(prompt_type.lower())
        if not cls:
            raise ValueError(
                f"Unknown prompt type '{prompt_type}'. "
                f"Available types: {', '.join(PromptFactory.registry.keys())}"
            )
        return cls(**kwargs)
