
import re
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from tools import *
import logging
from llm import LLM
from data_classes import AnalystOutput, LLMType
from tools import google_search


logging.basicConfig(level=logging.INFO) # Set the root logger level to INFO

class AnalystAgent():

    def __init__(self, system_prompt, iterations=5):

        self.messages = []
        self.iterations = iterations
        self.system_prompt = system_prompt
        
        tools = [google_search, arxiv_search, think_tool]
        self.llm = LLM(llm_type=LLMType.GEMINI, structured_output_class=AnalystOutput, tools=tools)

        self.action_re = re.compile(r"^(\w+)\[(.+)\]$")
        self.available_actions= {
            "google_search": google_search,
            "arxiv_search": arxiv_search,
            "think_tool": think_tool
        }

    def _thought(self, user_input):
        self.messages.append(HumanMessage(content=user_input))

        response = self.llm.invoke(self.messages)
        logging.info(f"\n\nthought response content ::\n {response}\n\n")
        self.messages.append(AIMessage(content=str(response)))
        return response


    def _action(self, response: AnalystOutput):

        tool, input = self._parse_result_for_actions(response.action)
        observation = None
        if tool and input:
            observation = tool.invoke(input)   
        logging.info(f"\nobservation: {observation}\n\n") 
        return observation
    

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
        while i < 5:
            action_output = self._action(response)
            if not action_output:
                break
            observation = "Observation: {}".format(action_output)
            response = self._thought(observation)
            i+=1
        return response


    def run(self, user_input: str, date_str: str):

        self.messages.clear()
        self.system_prompt = self.system_prompt.format(topic=user_input, date=date_str)
        self.messages.append(SystemMessage(content= self.system_prompt))      

        return self._react_loop(user_input)


