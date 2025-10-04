from langchain_community.utilities import GoogleSerperAPIWrapper
import time
from rag.knowledge_sources.abstract_datasource import AbstractDataSource
import logging
from typing import List
from langchain.chat_models import init_chat_model
import os
from langchain.schema import HumanMessage


logging.basicConfig(level=logging.INFO) # Set the root logger level to INFO

class LLMSource(AbstractDataSource):

    def __init__(self):
        self.llm = init_chat_model(model=os.getenv("OPENAI_MODEL"))


    def search(self, query: str) -> List[str]:
        

        results = []
        queries = query.split(",")        
        
        for query in queries:
            time.sleep(5)
            logging.info(f"\n\n-- running llm inference for  {query}")                        
            response = self.llm.invoke([{"role": "user", "content": f"Provide a detailed answer for the query: {query}"}])       
            results.append(response.content)

        return results

    def about(self) -> str:
        return "This is an LLM source that uses a language model for generating responses."

    def short_name(self) -> str:
        return "llm_source"