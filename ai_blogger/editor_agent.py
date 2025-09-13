
import re
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from tools import *
import logging
from llm import LLM
from data_classes import EditorOutput
from tools import google_search


logging.basicConfig(level=logging.INFO) # Set the root logger level to INFO

class EditorAgent():

    def __init__(self, system_prompt):

        self.messages = []

        self.system_prompt = system_prompt
        self.messages.append(SystemMessage(content= self.system_prompt))

        self.llm = LLM(structured_output_class=EditorOutput)
        #self.action_re = re.compile('^Action: (\w+): (.*)$')
        #self.action_re = re.compile(r'Action:\s*(\w+)\[\s*"([^"]+)"\s*\]')
        self.action_re = re.compile(r"^(\w+)\[(.+)\]$")
        self.available_actions= {
            "google_search": google_search,
            "arxiv_search": arxiv_search
            }


    def _thought(self, user_input):
        self.messages.append(HumanMessage(content=user_input))

        response = self.llm.invoke(self.messages)
        logging.info(f"\n\nthought response content :: {response}\n\n")
        self.messages.append(AIMessage(content=str(response)))
        return response


    def _action(self, response: EditorOutput):

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


    def run(self, user_input):
        i=0
        next_prompt = user_input
        response = self._thought(next_prompt)
        
        while i < 3:
            observation = self._action(response)
            response = self._thought(observation)
            i+=1
        
        # logging.info(f"\n\nresponse1: {response}")
        # response = self._thought(next_prompt)
        # logging.info(f"\n\nresponse2: {response}")
        # response = self._finalize(response)
        # logging.info(f"\n\nresponse3: {response}")
        return response


