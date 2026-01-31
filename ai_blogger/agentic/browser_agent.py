
"""
analyst agent read the summary and create a list of topics to be researched dumped in a file
editor agent reads the file and call researcher agent for each topic 1 by 1
researcer agent does the research on the topic passed to it and write the content to the file
blog writer agent reads the file and write the blog
each agent is a node in lang graph. each one of this is a react agent created using create_react_agent function in langgraph
"""

from prompts import *
from agents import Agent, Runner, OpenAIChatCompletionsModel
from structured_output import *
from tools import *
import os
import re
import json
from openai import AsyncOpenAI
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
            name="AI & LLM application Blogger",
            model=get_model(model_prefix),
            instructions=browser_prompt,
            tools=[file_writer, browse_urls]
        )
    

    def run(self, current_date, topic, content, file_name):
        result = Runner.run_sync(self.browser_agent, 
            f"current_date: {current_date}\n\n \
            topic: {topic}\n\n \
            urls: {str(content)}\n\n \
            file_name: {file_name}\n", max_turns=MAX_TURNS
        )

        return result


def browser(goal, user_input: list[str], file_name: str):
    
    agent = BrowserAgent(model_prefix="GEMINI")
    response = agent.run(
            topic=goal, content=user_input, current_date=current_date_str(), file_name=file_name
            )
    
    return response


if __name__ == "__main__":

    urls = [
        "https://github.com/sihyeong/Awesome-LLM-Inference-Engine",
        "https://multimodalai.substack.com/p/the-ai-engineers-guide-to-inference",
        "https://gautam75.medium.com/ten-ways-to-serve-large-language-models-a-comprehensive-guide-292250b02c11",
        "https://www.aleksagordic.com/blog/vllm",
        "https://medium.com/@martiniglesiasgo/anatomy-of-tgi-for-llm-inference-i-6ac8895d903d",
        "https://medium.com/@plienhar/llm-inference-series-1-introduction-9c78e56ef49d",
        "https://developer.nvidia.com/blog/mastering-llm-techniques-inference-optimization/",
        "https://oumi.ai/docs/en/latest/user_guides/infer/inference_engines.html"
    ]
    
    browser("Inference engine working", 
            urls, 
            "ai_blogger/agentic/blogs/inference_engine_working.md"
        )
