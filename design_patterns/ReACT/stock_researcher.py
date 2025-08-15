
from langchain_anthropic import ChatAnthropic
import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel
import re
from langchain_community.utilities import GoogleSerperAPIWrapper
from prompt import stock_research_prompt
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage


class DeepResearchAgent():

    def __init__(self, system_prompt):
        self.messages = []
        self.system_prompt = system_prompt

        self.messages.append(SystemMessage(content= self.system_prompt))

        self.llm = ChatAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"), 
                                 model=os.getenv("ANTHROPIC_MODEL"),
                                 base_url=os.getenv("ANTHROPIC_BASE_URL"))
        self.action_re = re.compile('^Action: (\w+): (.*)$')
        self.google_serper = GoogleSerperAPIWrapper()
        self.available_actions= {"google_search": self._google_search}


    def _thought(self, user_input):
        self.messages.append(HumanMessage(content= user_input))

        response = self.llm.invoke(self.messages)
        self.messages.append(AIMessage(content= response))
        return response


    def _parse_result_for_actions(self, result):
        actions = [self.action_re.match(a) for a in result.split('\n') if self.action_re.match(a)]
        if actions:
            action, action_input = actions[0].groups()
            
            if action not in self.available_actions:
                raise Exception("Unknown action: {}: {}".format(action, action_input))
            
            print(" -- running {} {}".format(action, action_input))
            action = self.available_actions[action]
            return action, action_input
        else:
            return


    def _google_search(self, query):
        result = self.google_serper.search(query)
        return result


    def _perform_action(self, action, action_input):
        observation = action(action_input)
        print("Observation:", observation)
        next_prompt = "Observation: {}".format(observation)
        return next_prompt


    def run(self, user_input):
        i =0
        next_prompt = user_input
        response=""
        while i < 5:
            response = self._thought(next_prompt)
            action, action_input = self._parse_result_for_actions(result=response)
            next_prompt = self._perform_action(action=action, action_input=action_input)
        return response


if __name__ == '__main__':

    load_dotenv(override=True)
    user_input = input("Enter your stock research query: ")
    agent = DeepResearchAgent(stock_research_prompt)
    response = agent.run(user_input=user_input)
    print(f"\n\n final response: \n\n {response}")

