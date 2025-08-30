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
from deep_agent_prompt import system_prompt
from langgraph.prebuilt.tool_node import ToolNode
from typing import List
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.tools import Tool

class Action(BaseModel):
    action_name: str
    args: str

class ReACTResponse(BaseModel):
    Thought: str
    action_list: List[Action]

class FinalDesign(BaseModel):
    project_short_name: str
    solution_approach: str
    architecure_diagram: str
    design_patterns: str
    llm_sdk_tools_frameworks: str
    detailed_design: str
    prompting_technique: str
    github_links: str

class DeepAgentState(TypedDict):
    input: str
    results: ReACTResponse
    observations: List[str]
    counter: int = 1
    final_design: FinalDesign


class DeepAgent:

    def __init__(self, llm_client, user_prompt: str, tools: List[ToolNode]=[] ):
        
        self.llm = llm_client
        self.user_prompt = user_prompt
        self.messages = []
        self.tool_llm = None
        self.counter = 0
        
        self.google_serper = GoogleSerperAPIWrapper()
        search_tool = Tool(
            name="google_search", 
            func=self.google_serper.run,
            description="Search the web for relevant information",)
        
        self.tools = [search_tool]


    def execute(self, state: DeepAgentState):

        self.messages.append(SystemMessage(content=system_prompt))
        self.messages.append(HumanMessage(content=state["input"]))
                             
        messages = [
                SystemMessage(content=system_prompt),
                ("placeholder", "{messages}"),
            ]
        
        prompt_template = ChatPromptTemplate.from_messages(messages)

        self.tool_llm = self.llm.bind_tools(self.tools)
       
        prompt_llm = prompt_template | self.tool_llm.with_structured_output(ReACTResponse)

        result = prompt_llm.invoke({"messages": 
            [
                HumanMessage(state["input"])
            ]
        })

        print(f"\n results :: {result}\n")
        self.messages.append(AIMessage(content=str(result)))
        return {"results": result}


    def parse_results(self, state: DeepAgentState):
        
        observations = []
        for action in state["results"].action_list:
            print(f"\n\n-- running {action.action_name} {action.args}\n\n")
            tool = next((tool for tool in self.tools if tool.name == action.action_name), None)
            if tool:
                observation = tool.run(action.args)
                print(f"\n\nTool Response: {observation}\n\n")
                observations.append(observation)
                time.sleep(3)
        return {"observations": observations}


    def observe(self, state: DeepAgentState):
        self.counter+=1
        all_observations = "\n".join(state["observations"])
        self.messages.append(HumanMessage(content=all_observations))
        
        llm = self.tool_llm.with_structured_output(ReACTResponse)

        response = llm.invoke(self.messages)

        print(f"\n\nObservation Response: {response}\n\n")
        self.messages.append(AIMessage(content=str(response)))
        return {"results": response}


    def final_response(self, state: DeepAgentState):
        all_observations = "\n".join(state["observations"])
        self.messages.append(HumanMessage(content=all_observations))
        
        llm = self.llm.with_structured_output(FinalDesign)

        response = llm.invoke(self.messages)
        print("\n=================================================================================================\n")
        print(f"\n\nFinal Response: {response}\n\n")
        self.messages.append(AIMessage(content=str(response)))
        return {"final_design": response}


    def write_final_design_to_markdown(self, state: DeepAgentState):
        """
        Writes the final_design from DeepAgentState to a markdown file.
        Args:
            state (DeepAgentState): The agent state containing final_design.
            filename (str): The markdown file to write to.
        """
        final_design = state.get("final_design")
        if not final_design:
            print("No final_design found in state.")
            return
        
        file_name = state["final_design"].project_short_name.replace(" ", "_").lower()
        filename = f"./ai_solution_architect/output/{file_name}_solution_architecture.md"

        md_content = f"""
# Solution Architecture

## Approach
{final_design.solution_approach}

## Architecture Diagram
{final_design.architecure_diagram}

## Design Patterns
{final_design.design_patterns}

## LLM, SDKs, Tools, Frameworks
{final_design.llm_sdk_tools_frameworks}

## Detailed Design
{final_design.detailed_design}

## Prompting Technique
{final_design.prompting_technique}

## GitHub Links
{final_design.github_links}
"""

        with open(filename, "w", encoding="utf-8") as f:
            f.write(md_content)


    def should_continue(self, state: DeepAgentState):
        if self.counter >= 3:
            return "final_response"
        return "parse_results"

    def build_graph(self):
        graph = StateGraph(DeepAgentState)
        graph.add_node("execute", self.execute)
        graph.add_node("parse_results", self.parse_results)
        graph.add_node("observe", self.observe)
        graph.add_node("final_response", self.final_response)
        graph.add_node("write_final_design_to_markdown", self.write_final_design_to_markdown)

        graph.add_edge(START, "execute")
        graph.add_edge("execute", "parse_results")
        graph.add_edge("parse_results", "observe")
        graph.add_conditional_edges("observe", self.should_continue, 
                {
                    "final_response": "final_response",
                    "parse_results": "parse_results",                    
                })
        graph.add_edge("final_response", "write_final_design_to_markdown")

        app = graph.compile()
        app.get_graph().print_ascii()
        return app

    
# Example usage after agent run:
def run():
    load_dotenv(override=True)
    
    llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model=os.getenv("OPENAI_MODEL"))
    tools = [TavilySearchResults(max_results=5)]
    
    agent = DeepAgent(llm, None, tools)    
    app = agent.build_graph()

    config = {"recursion_limit": 10}

    #user_input = "Build a chat bot that can answer questions about the stock market"
    #user_input = "Build a rag agent"
    user_input = "Coding agent that can write, debug and explain code"
    inputs = {"input": user_input }
    #inputs = HumanMessage("Agentic AI Design Pattern: Reflection" )
    response = app.invoke(input=inputs, config=config)

if __name__ == "__main__":
    run()