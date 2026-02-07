
"""
analyst agent read the summary and create a list of topics to be researched dumped in a file
editor agent reads the file and call researcher agent for each topic 1 by 1
researcer agent does the research on the topic passed to it and write the content to the file
blog writer agent reads the file and write the blog
each agent is a node in lang graph. each one of this is a react agent created using create_react_agent function in langgraph
"""

from prompts import browser_agent_prompt
from agents import Agent, Runner, OpenAIChatCompletionsModel
from tools import *
import os
from agents.extensions.models.litellm_model import LitellmModel
from dotenv import load_dotenv
import logging
from utils import *


load_dotenv(override=True)
logging.basicConfig(level=logging.INFO) # Set the root logger level to INFO
MAX_TURNS = 7


def get_model(prefix= "OPENAI"):        

    model = os.getenv(prefix+"_MODEL")
    api_key = os.getenv(prefix+"_API_KEY")
    base_url = os.getenv(prefix+"_BASE_URL")

    return LitellmModel(model=model, api_key=api_key)
        

class BrowserAgent:
        
    def __init__(self, model_prefix="OPENAI"):

        print(f"Browser agent using {model_prefix} model")    
        self.browser_agent = Agent(
            name="Browser Agent",
            model=get_model(model_prefix),
            instructions=browser_agent_prompt,
            tools=[browse_urls]
        )
    

    def run(self, current_date, topic, content, file_name):
        result = Runner.run_sync(self.browser_agent, 
            f"current_date: {current_date}\n\n \
            topic: {topic}\n\n \
            urls: {str(content)}\n\n \
            file_name: {file_name}\n", max_turns=MAX_TURNS
        )

        return result


