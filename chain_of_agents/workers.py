from data_classes import InformationChunk, WrokerAgentResult
from prompts import *
from llm import LLM
from dotenv import load_dotenv

class WorkerAgent:
    
    def __init__(self, name: str, goal: str, system_prompt: str, document_chunk: InformationChunk, previous_result: str = None):
        load_dotenv(override=True)
        self.name = name
        self.goal = goal
        self.system_prompt = system_prompt
        self.document_chunk = document_chunk
        self.previous_result = previous_result
        self.llm = LLM(WrokerAgentResult)

    def _create_prompts(self) -> tuple[str, str]:     

        system_promt = worker_system_message.format(index=self.name)
        user_prompt = worker_user_prompt.format(user_goal=self.goal, 
                                                previous_cu=self.previous_result or "No previous findings available.", 
                                                content=self.document_chunk.content)

        return system_promt, user_prompt

    def perform_task(self) -> WrokerAgentResult:

        system_prompt, user_prompt = self._create_prompts()
        response = self.llm.invoke(system_prompt, user_prompt)

        print(f"\n Worker {self.name} is performing task on chunk: {self.document_chunk} with previous result: {response.previous_result[:100] if self.previous_result else None}... \n result: {response.current_result[:100]}...\n")
        print("=============================================================================================================================================")
        return response 

        