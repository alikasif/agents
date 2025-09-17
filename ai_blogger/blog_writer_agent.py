
import re
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from tools import *
import logging
from llm import LLM
from data_classes import LLMType

logging.basicConfig(level=logging.INFO) # Set the root logger level to INFO

class BloggerAgent():


    def __init__(self, system_prompt, user_input):

        self.messages = []
        self.user_input = user_input
        self.system_prompt = system_prompt
        self.messages.append(SystemMessage(content=self.system_prompt))

        self.llm = LLM(llm_type=LLMType.OPEN_AI)


    def write_blog(self):
        
        #self.messages.append(HumanMessage(content=content))
        response = self.llm.invoke(self.messages)
        #logging.info(f"\n\nblog :: {response}\n\n")

        # Append the response to blog.md
        with open("./ai_blogger/blog.md", "a", encoding="utf-8") as f:
            f.write(f"{response.content}\n\n")
    