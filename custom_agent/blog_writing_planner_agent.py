from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
import os, time
from dotenv import load_dotenv
from typing_extensions import TypedDict
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from prompt import blog_plan_template, blog_execute_template, blog_review_template
from langgraph.prebuilt.tool_node import ToolNode
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_community.utilities import GoogleSerperAPIWrapper

class PlanExecute(TypedDict):
    input: str
    plan_string: str
    steps: List[str]
    research_summary: str
    refined_blog: str

class ResearchPlan(BaseModel):
    plan_string: str
    steps: List[str]

class PromptGeneration(BaseModel):
    prompt: str

class Research(BaseModel):
    blog: str

class Review(BaseModel):
    refined_blog: str

class Refined(BaseModel):
    refined_summary: str

class GoogleSearchResults(BaseModel):
    search_summary: str


class DeepBlogAgent:
    

    def __init__(self):
        self.tools = [TavilySearchResults(max_results=5)]
        self.llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model=os.getenv("OPENAI_MODEL"))
        #self.llm = ChatGoogleGenerativeAI(model=os.getenv("GOOGLE_MODEL"))
        self.parser = StrOutputParser()
        self.search = GoogleSerperAPIWrapper()


    def planner(self, state: PlanExecute):

        messages = [
                SystemMessage(
                    content=blog_plan_template
                ),
                ("placeholder", "{messages}"),
        ]
        plan_template = ChatPromptTemplate.from_messages(messages)
        
        prompt_llm = self.llm.bind_tools(self.tools)
        prompt_llm = plan_template | prompt_llm.with_structured_output(ResearchPlan)
        
        result = prompt_llm.invoke({"messages": [
                    HumanMessage(state["input"])
            ]})
        #print(f"\n\n {result}\n\n")
        return {"plan_string": result.plan_string, "steps": result.steps}


    def execute(self, state: PlanExecute):
        
        all_steps = "\n".join(state['steps'])
        messages = [
                SystemMessage(
                    content=blog_execute_template
                ),
                ("placeholder", "{messages}"),
        ]
        execute_template = ChatPromptTemplate.from_messages(messages)
        
        execute_llm = self.llm.bind_tools(self.tools)
        execute_llm = execute_template | execute_llm.with_structured_output(Research)
        
        result = execute_llm.invoke({"messages": [
                    HumanMessage(all_steps)
            ]})
        
        return {"research_summary": result.blog}


    def review(self, state: PlanExecute):
        
        messages = [
                SystemMessage(
                    content=blog_review_template
                ),
                ("placeholder", "{messages}"),
        ]
        execute_template = ChatPromptTemplate.from_messages(messages)
        
        execute_llm = self.llm.bind_tools(self.tools)
        execute_llm = execute_template | execute_llm.with_structured_output(Review)
        
        result = execute_llm.invoke({"messages": [
                    HumanMessage(state["research_summary"])
            ]})
        
        return {"refined_blog": result.refined_blog}


    def print_results(self, state: PlanExecute):
        print(f"\n\n Final Results: \n\n \
              plan_string :: {state['plan_string']} \n \
============================================================================================================================================== \n \
              steps :: {state['steps']} \n\
============================================================================================================================================== \n \
              research_summary :: {state['research_summary']} \n\
============================================================================================================================================== \n \
              **refined_blog** :: {state['refined_blog']} \n\
============================================================================================================================================== \n \
              ")


    def build_graph(self):

        workflow = StateGraph(PlanExecute)
        
        # search_tool_node = ToolNode(self.tools)
        # workflow.add_node("web_search", search_tool_node)

        # Add the plan node
        workflow.add_node("planner", self.planner)
        workflow.add_node("execute", self.execute)
        workflow.add_node("review", self.review)
        workflow.add_node("print_results", self.print_results)
        
        # add edges
        workflow.add_edge(START, "planner")
        workflow.add_edge("planner", "execute")
        workflow.add_edge("execute", "review")
        workflow.add_edge("review", "print_results")

        app = workflow.compile()

        try:    
            app.get_graph().print_ascii()
        except Exception as e:
            print(str(e))

        return app


    def run(self):
        app = self.build_graph()

        config = {"recursion_limit": 10}

        inputs = {"input": "Agentic AI Design Pattern: Reflection" }
        #inputs = HumanMessage("Agentic AI Design Pattern: Reflection" )
        response = app.invoke(input=inputs, config=config)


if __name__ == "__main__":
    load_dotenv(override=True)
    deep_agent = DeepBlogAgent()
    deep_agent.run()




