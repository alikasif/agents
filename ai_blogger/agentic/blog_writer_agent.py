
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

MAX_TURNS = 7

def get_model(prefix= "OPENAI"):        

    model = os.getenv(prefix+"_MODEL")
    api_key = os.getenv(prefix+"_API_KEY")
    base_url = os.getenv(prefix+"_BASE_URL")

    return LitellmModel(model=model, api_key=api_key)
        
        # if prefix == "OPENAI":
        #     return os.getenv(prefix+"_MODEL")
        
        # external_client = AsyncOpenAI(
        #     api_key=os.getenv(prefix+"_API_KEY"),
        #     base_url=os.getenv(prefix+"_BASE_URL")
        # )
        # return OpenAIChatCompletionsModel(model=os.getenv(prefix+"_MODEL"), openai_client=external_client)


class AnalystAgent:
    
    def __init__(self, model_prefix="OPENAI"):

        print(f"Analyst agent using {model_prefix} model")    
        self.analyst_agent = Agent(
            name="AI & LLM application analyst",
            model=get_model(model_prefix),
            instructions=analyst_prompt,
            output_type=Outline,            
            # Don't use output_type for Anthropic - it doesn't follow JSON mode
            tools=[google_search, file_writer, browse]
        )
    
    def run(self, current_date, topic, content, file_name):
        result = Runner.run_sync(self.analyst_agent, 
            f"current_date: {current_date}\n\n \
            topic: {topic}\n\n \
            content: {str(content)}\n\n \
            file_name: {file_name}\n", max_turns=MAX_TURNS
        )

        return result


class ResearchAgent:

    def __init__(self, model_prefix="OPENAI"):    
        print(f"Research agent using {model_prefix} model")    
        self.researcher_agent = Agent(
            name="Senior AI Researcher",
            model=get_model(model_prefix),
            instructions=research_prompt,
            output_type=ResearchOutput,
            # Don't use output_type for Anthropic - it doesn't follow JSON mode
            tools=[google_search, browse]
        )
    
    def prepare_input(self, topic: Topic):
        query = f"""
                Topic: {topic.topic}
                \n
                Subtopics:
                {chr(10).join(f"- {s}" for s in topic.sub_topics)}
                \n
                Content:
                {topic.content}
                """
        return query


    def run(self, topic: Topic):
        result = Runner.run_sync(self.researcher_agent, f"content: {self.prepare_input(topic)}", max_turns=MAX_TURNS)
        return result.final_output
       

class BloggerAgent:
    def __init__(self, model_prefix="OPENAI"):    
        print(f"Blogger agent using {model_prefix} model")    
        
        self.blogger_agent = Agent(
            name="AI/LLM Technical Blogger",
            model=get_model(model_prefix),
            instructions=blogger_prompt,
            tools=[google_search, blog_writer, browse]
        )

    def run(self, blog_name: str, research: str):
        result = Runner.run_sync(self.blogger_agent, f"blog_name: {blog_name}\n\nresearch: {research}", max_turns=MAX_TURNS)
        return result.final_output


class EditorAgent:
    def __init__(self, model_prefix="OPENAI"):    
        print(f"Editor agent using {model_prefix} model")    
        self.editor_agent = Agent(
            name="AI/LLM Technical Editor",
            model=get_model(model_prefix),
            instructions=editor_prompt,
            tools=[google_search, blog_writer, browse]
        )

    def run(self, blog_name: str, blog: str):
        result = Runner.run_sync(self.editor_agent, f"blog_name: {blog_name}\n\nblog: {blog}", max_turns=MAX_TURNS)
        return result.final_output
