from chunker import Chunker
from workers import WorkerAgent 
from data_classes import InformationChunk
from llm import LLM
import os
import time
from prompts import manager_system_message, manager_user_prompt
from dotenv import load_dotenv

class ManagerAgent:

    def __init__(self,  user_goal: str):
        load_dotenv(override=True)
        self.user_goal = user_goal
        self.llm = LLM()


    def _create_prompts(self, final_result) -> tuple[str, str]:     

        system_promt = manager_system_message
        user_prompt = manager_user_prompt.format(user_goal=self.user_goal, 
                                                final_result=final_result or "No findings available.")

        return system_promt, user_prompt


    def finalize_results(self, final_result) -> str:
        """Processes the entire document and returns the final summary."""
        system_prompt, user_prompt = self._create_prompts(final_result)
        summary = self.llm.invoke(system_prompt, user_prompt)
        return summary.content
