
import re
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from tools import *
import logging
from llm import LLM

logging.basicConfig(level=logging.INFO) # Set the root logger level to INFO

class BloggerAgent():

    def __init__(self, system_prompt):

        self.messages = []

        self.system_prompt = system_prompt
        self.messages.append(SystemMessage(content= self.system_prompt))

        self.llm = LLM()
        #self.action_re = re.compile('^Action: (\w+): (.*)$')
        self.action_re = re.compile(r'Action:\s*(\w+)\[\s*"([^"]+)"\s*\]')
        self.available_actions= {
            "google_search": google_search,
            "arxiv_search": arxiv_search
            }


    def _thought(self, user_input):
        self.messages.append(HumanMessage(content=user_input))

        response = self.llm.invoke(self.messages)
        #logging.info(f"\n\nthought response content :: {response.content}\n\n")
        self.messages.append(AIMessage(content=response.content))
        return response.content

    def _finalize(self, user_input):
        self.messages.append(HumanMessage(content=user_input))

        response = self.llm.invoke(self.messages)
        #logging.info(f"\n\nthought response content :: {response.content}\n\n")
        self.messages.append(AIMessage(content=response.content))
        return response.content


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


    def _perform_action(self, action, action_input):
        observation = action(action_input)
        #print("\n\nObservation:", observation)
        next_prompt = "Observation: {}".format(observation)
        return next_prompt


    def run(self, user_input):
        i =0
        next_prompt = user_input
        response = self._thought(next_prompt)
        logging.info(f"\n\nthought:: {response}\n\n")
        
        while i < 5:
            action, action_input = self._parse_result_for_actions(result=response)
            if action:
                #logging.info(f"\n\naction = {action} action_input = {action_input}")
                next_prompt = self._perform_action(action=action, action_input=action_input)
                response = self._thought(next_prompt)
                #logging.info(f"\n\nnext prompt {next_prompt}")
            else:
                logging.warning(f"*** NO ACTION FOUND!!")
            i+=1
        
        # logging.info(f"\n\nresponse1: {response}")
        # response = self._thought(next_prompt)
        # logging.info(f"\n\nresponse2: {response}")
        # response = self._finalize(response)
        # logging.info(f"\n\nresponse3: {response}")
        return response


