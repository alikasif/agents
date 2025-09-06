"""
manager will get the document to process along with a goal prompt. its job is to split the document into chunks,
create worker agents for each chunk, and manage the flow of information between them.
"""

from chunker import Chunker
from workers import WorkerAgent 
from data_classes import InformationChunk
from llm import LLM
import os
import time
from prompts import manager_system_message, manager_user_prompt
from dotenv import load_dotenv

class ManagerAgent:

    def __init__(self, document_path: str, user_goal: str, chunk_size: int = 1000, start_page: int = 0):
        load_dotenv(override=True)
        self.document_path = document_path
        self.user_goal = user_goal
        self.chunker = Chunker(chunk_size, start_page)
        self.llm = LLM()
        self.worker_agents = [WorkerAgent]
        self.final_result = ""
        self.document_chunks = [InformationChunk]


    def create_prompts(self) -> tuple[str, str]:     

        system_promt = manager_system_message
        user_prompt = manager_user_prompt.format(user_goal=self.user_goal, 
                                                final_result=self.final_result or "No findings available.")

        return system_promt, user_prompt


    def _create_chunks(self) -> list[InformationChunk]:
        """Splits the document into chunks."""
        self.document_chunks = self.chunker.chunk(self.document_path)
        print(f"Document split into {len(self.document_chunks)} chunks.")


    def _process_next_chunk(self, chunk_index: int, chunk: InformationChunk, previous_result: str = None) -> str:
        """Processes a single chunk using a worker agent."""
        worker = WorkerAgent(
            name=f"Worker-{chunk_index}",
            goal=self.user_goal,
            system_prompt=manager_system_message,
            document_chunk=chunk,
            previous_result=previous_result
        )
        result = worker.perform_task()
        return result


    def _start_chain_of_agents(self):
        """Starts the chain of agents to process the document."""

        for idx, chunk in enumerate(self.document_chunks):
            previous_result = self.final_result if idx > 0 else None
            result = self._process_next_chunk(idx + 1, chunk, previous_result)
            self.final_result += f"\n{result.current_result}\n"
            time.sleep(1)  # To avoid rate limiting


    def _finalize_results(self) -> str:
        """Processes the entire document and returns the final summary."""
        system_prompt, user_prompt = self.create_prompts()
        summary = self.llm.invoke(system_prompt, user_prompt)
        return summary

    
    def execute(self) -> str:
        """Executes the manager agent workflow."""
        self._create_chunks()
        self._start_chain_of_agents()        
        summary = self._finalize_results()
        #print(f"\nFinal Summary:\n{summary}\n")
        return summary
    
