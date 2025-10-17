
"""
analyst agent read the summary and create a list of topics to be researched dumped in a file

editor agent reads the file and call researcher agent for each topic 1 by 1

researcer agent does the research on the topic passed to it and write the content to the file

blog writer agent reads the file and write the blog

each agent is a node in lang graph. each one of this is a react agent created using create_react_agent function in langgraph

"""

from agents import Agent
from prompts import *
from agents import Agent, Runner, OpenAIChatCompletionsModel
from structured_output import *
from tools import *
import os
from openai import AsyncOpenAI
from agents.agent_output import AgentOutputSchema


def get_model(prefix= "OPENAI"):        
        
        if prefix == "OPENAI":
            return os.getenv(prefix+"_MODEL")
        
        external_client = AsyncOpenAI(
            api_key=os.getenv(prefix+"_API_KEY"),
            base_url=os.getenv(prefix+"_BASE_URL")
        )
        return OpenAIChatCompletionsModel(model=os.getenv(prefix+"_MODEL"), openai_client=external_client)


class AnalystAgent:
    def __init__(self):        
        self.analyst_agent = Agent(
            name="AI & LLM application analyst",
            model=get_model(),
            instructions=analyst_prompt,
            output_type=Outline,
            tools=[google_search]
        )
    
    async def run(self, current_date, topic, content):
        result = await Runner.run(self.analyst_agent, f"current_date: {current_date}\n\ntopic: {topic}\n\ncontent: {str(content)}\n")
        return result.final_output


class ResearchAgent:    
    def __init__(self):        
        self.researcher_agent = Agent(
            name="Senior AI Researcher",
            model=get_model(),
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
        result = await Runner.run(self.researcher_agent, f"content: {self.prepare_input(topic)}")
        return result.final_output


class BloggerAgent:
    def __init__(self):        
        self.blogger_agent = Agent(
            name="AI/LLM Technical Blogger",
            model=get_model("GEMINI"),
            instructions=blogger_prompt,
            tools=[google_search]
        )

    async def run(self, research: str):
        result = await Runner.run(self.blogger_agent, f"research: {research}")
        return result.final_output


class EditorAgent:
    def __init__(self):        
        # Create an asynchronous OpenAI-style client for calling external APIs (e.g., Gemini)
        
        self.editor_agent = Agent(
            name="AI/LLM Technical Editor",
            model=get_model("ANTHROPIC"),
            instructions=editor_prompt,
            tools=[google_search]
        )

    async def run(self, research: str):
        result = await Runner.run(self.editor_agent, f"blog: {research}")
        return result.final_output
