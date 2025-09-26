
"""
analyst agent read the summary and create a list of topics to be researched dumped in a file

editor agent reads the file and call researcher agent for each topic 1 by 1

researcer agent does the research on the topic passed to it and write the content to the file

blog writer agent reads the file and write the blog

each agent is a node in lang graph. each one of this is a react agent created using create_react_agent function in langgraph

"""

from agents import Agent
from prompts import *
from agents import Agent, Runner
from structured_output import *
from tools import *
import os

class AnalystAgent:
    def __init__(self):        
        self.analyst_agent = Agent(
            name="AI & LLM application analyst",
            model=os.getenv("OPENAI_MODEL"),
            instructions=analyst_prompt,
            output_type=Outline,
            tools=[google_search]
        )
    
    async def run(self, current_date, topic, content):
        result = await Runner.run(self.analyst_agent, f"current_date: {current_date}\n\ntopic: {topic}\n\ncontent: {content}\n")
        return result.final_output


class ResearchAgent:
    
    def __init__(self):        
        self.analyst_agent = Agent(
            name="Senior AI Researcher",
            instructions=research_prompt,
            output_type=ResearchOutput,
            tools=[google_search]
        )
    
    def prepare_input(self, topic: Topic):
        query = f"""
                Topic: {topic.topic}
                \n
                Subtopics:
                {chr(10).join(f"- {s}" for s in topic.sub_topics)}
                """
        return query


    async def run(self, topic: Topic):
        result = await Runner.run(self.analyst_agent, f"content: {self.prepare_input(topic)}")
        return result.final_output


class BloggerAgent:
    def __init__(self):        
        self.analyst_agent = Agent(
            name="AI/LLM Technical Blogger",
            instructions=blogger_prompt,
            tools=[google_search]
        )

    async def run(self, research: str):
        result = await Runner.run(self.analyst_agent, f"research: {research}")
        return result.final_output