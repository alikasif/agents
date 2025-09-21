from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool

import os
from langchain_core.prompts import ChatPromptTemplate
from data_classes import LLMType

class LLM:

    def __init__(self, llm_type: LLMType = LLMType.OPEN_AI, structured_output_class: type = None, tools=None):

        self.llm = None
        if llm_type == LLMType.OPEN_AI:
            self.llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL"))
        elif llm_type == LLMType.GEMINI:
            self.llm = ChatGoogleGenerativeAI(model=os.getenv("GOOGLE_MODEL"))
        else:
            raise("LLM type missing!!")

        self.llm = self.llm if not tools else self.llm.bind_tools(tools)
        self.llm = self.llm if not structured_output_class else self.llm.with_structured_output(structured_output_class)

    def invoke(self, messages: list) -> str:
        
        prompt_template = ChatPromptTemplate.from_messages(messages)

       
        prompt_llm = prompt_template | self.llm

        result = prompt_llm.invoke({})
            
        # Placeholder for actual LLM API call
        return result