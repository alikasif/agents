from langchain_openai import ChatOpenAI
import os
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

class LLM:

    def __init__(self, structured_output_class: type = None):
        self.llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model=os.getenv("OPENAI_MODEL"))
        self.llm = self.llm if not structured_output_class else self.llm.with_structured_output(structured_output_class)

    def invoke(self, messages: list) -> str:
        
        prompt_template = ChatPromptTemplate.from_messages(messages)

       
        prompt_llm = prompt_template | self.llm

        result = prompt_llm.invoke({})
            
        # Placeholder for actual LLM API call
        return result
