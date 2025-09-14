
import re
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from tools import *
import logging
from llm import LLM
from data_classes import ResearcherOutput
from tools import google_search
from langchain.prompts import PromptTemplate
from pprint import pprint

logging.basicConfig(level=logging.INFO) # Set the root logger level to INFO


class ResearcherAgent():

    def __init__(self, system_prompt: PromptTemplate):

        self.messages = []

        self.system_prompt = system_prompt
        tools = [google_search, arxiv_search, think_tool]
        self.llm = LLM(structured_output_class=ResearcherOutput, tools=tools)

        self.action_re = re.compile(r"^(\w+)\[(.+)\]$")
        self.available_actions= {
            "google_search": google_search,
            "arxiv_search": arxiv_search,
            "think_tool": think_tool
        }
        

    def _thought(self, user_input):
        self.messages.append(HumanMessage(content=user_input))

        response = self.llm.invoke(self.messages)
        logging.info(f"\n\nthought response content :: {response}\n\n")
        self.messages.append(AIMessage(content=str(response)))
        return response


    def _action(self, response: ResearcherOutput):

        tool, input = self._parse_result_for_actions(response.action)
        observation = ""
        if tool and input:
            observation = tool(input)   
        logging.info(f"\nobservation: {observation}\n\n") 
        next_prompt = "Observation: {}".format(observation)
        return next_prompt
    

    def _parse_result_for_actions(self, result):
        actions = [self.action_re.match(a) for a in result.split('\n') if self.action_re.match(a)]
        if actions:
            action, action_input = actions[0].groups()
            
            if action not in self.available_actions:
                raise Exception("Unknown action: {}: {}".format(action, action_input))
            
            action = self.available_actions[action]
            return action, action_input
        else:
            return None, None


    def _react_loop(self, user_input):
        i=0
        response = self._thought(user_input)        
        while i < 3:
            observation = self._action(response)
            response = self._thought(observation)
            i+=1
        return response


    def run(self, user_input: str, date_str: str):

        self.messages.clear()
        self.system_prompt = self.system_prompt.format(topic=user_input, date=date_str)
        self.messages.append(SystemMessage(content= self.system_prompt))      

        return self._react_loop(user_input)



