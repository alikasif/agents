from dotenv import load_dotenv
from agent import BloggerAgent
from prompt import deep_research_notebook_prompt

import logging

logging.basicConfig(level=logging.INFO) # Set the root logger level to INFO

load_dotenv(override=True)
user_input = input("Enter your research query: ")
prompt= deep_research_notebook_prompt.format(topic=user_input)
agent = BloggerAgent(prompt)
response = agent.run(user_input=user_input)
print(f"\n\n final response: \n\n {response}")

