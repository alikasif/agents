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
from prompt import research_prompt, review_prompt, refine_prompt
from langgraph.prebuilt.tool_node import ToolNode
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_community.utilities import GoogleSerperAPIWrapper

class PlanExecute(TypedDict):
    input: str
    research_summary: str
    feedback: str
    google_searches: List[str]
    google_search_results: str
    refined_summary: str

class Research(BaseModel):
    research_summary: str
    google_searches: List[str]

class Review(BaseModel):
    review_comments: str

class Refined(BaseModel):
    refined_summary: str

class GoogleSearchResults(BaseModel):
    search_summary: str


class DeepAgent:
    
    def __init__(self):
        self.tools = [TavilySearchResults(max_results=5)]
        #self.llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model=os.getenv("OPENAI_MODEL"))
        self.llm = ChatGoogleGenerativeAI(model=os.getenv("GOOGLE_MODEL"))
        self.parser = StrOutputParser()
        self.search = GoogleSerperAPIWrapper()


    def research(self, state: PlanExecute):
        messages = [
                SystemMessage(
                    content=research_prompt
                ),
                ("placeholder", "{messages}"),
        ]
        research_prompt_template = ChatPromptTemplate.from_messages(messages)
        
        research_llm = self.llm.bind_tools(self.tools)
        researcher = research_prompt_template | research_llm.with_structured_output(Research)
        
        #print(f"\n\n {state['input']}\n\n")
        #result = researcher.invoke(HumanMessage(state["input"]))
        result = researcher.invoke({"messages": [HumanMessage(state["input"])]})
        #print(f"\n\n {result}\n\n")
        return {"research_summary": result.research_summary, "google_searches": result.google_searches}

    def critic(self, state: PlanExecute):
        
        messages = [
                SystemMessage(
                    content=review_prompt
                ),
                ("placeholder", "{messages}"),
        ]
        review_prompt_template = ChatPromptTemplate.from_messages(messages)
        reviewer = review_prompt_template | self.llm.with_structured_output(Review)
        result = reviewer.invoke({"messages": [
            HumanMessage(state["input"]), 
            HumanMessage(state["research_summary"])
            ]})
        return {"feedback": result.review_comments}


    def google_search(self, state: PlanExecute):

        search_results = []
        for query in state["google_searches"]:
            time.sleep(5)
            results = self.search.run(query)
            search_results.append(results)
        
        return {"google_search_results": "".join(search_results)}


    def refine(self, state: PlanExecute):
        messages = [
                SystemMessage(
                    content=refine_prompt
                ),
                ("placeholder", "{messages}"),
        ]
        refine_prompt_template = ChatPromptTemplate.from_messages(messages)
        refiner = refine_prompt_template | self.llm.with_structured_output(Refined)
        
        if not state["google_search_results"]:
            raise ValueError("No google search results found")
        
        result = refiner.invoke({"messages": [
            HumanMessage(state["input"]), 
            HumanMessage(state["research_summary"]), 
            HumanMessage(state["feedback"]),
            HumanMessage(state["google_search_results"]),
            ]})
        
        return {"refined_summary": result.refined_summary}
        

    def write(self):
        pass

    def reevaluate(self):
        pass

    def print_results(self, state: PlanExecute):
        print(f"\n\n Final Results: \n\n \
              research_summary :: {state['research_summary']} \n \
============================================================================================================================================== \n \
              google_searches :: {state['google_searches']} \n\
============================================================================================================================================== \n \
              feedback :: {state['feedback']} \n\
============================================================================================================================================== \n \
              google_search_results :: {state['google_search_results']} \n\
============================================================================================================================================== \n \
              refined_summary :: {state['refined_summary']} \n\
============================================================================================================================================== \n \
              ")


    def build_graph(self):

        workflow = StateGraph(PlanExecute)
        
        # search_tool_node = ToolNode(self.tools)
        # workflow.add_node("web_search", search_tool_node)

        # Add the plan node
        workflow.add_node("researcher", self.research)
        workflow.add_node("reviewer", self.critic)
        workflow.add_node("refiner", self.refine)
        workflow.add_node("google_search", self.google_search)
        workflow.add_node("print_results", self.print_results)
        
        # add edges
        workflow.add_edge(START, "researcher")
        workflow.add_edge("researcher", "reviewer")
        workflow.add_edge("researcher", "google_search")
        workflow.add_edge("reviewer", "refiner")
        workflow.add_edge("google_search", "refiner")
        workflow.add_edge("refiner", "print_results")

        app = workflow.compile()

        try:    
            app.get_graph().print_ascii()
        except Exception as e:
            print(str(e))

        return app
    
    def run(self):
        app = self.build_graph()

        config = {"recursion_limit": 5}

        inputs = {"input": "Agentic AI Design Pattern: Reflection" }
        #inputs = HumanMessage("Agentic AI Design Pattern: Reflection" )
        response = app.invoke(input=inputs, config=config)


if __name__ == "__main__":
    load_dotenv(override=True)
    deep_agent = DeepAgent()
    deep_agent.run()




