from typing_extensions import List
from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
import os, time
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from deep_agent_prompt import system_prompt, review_prompt, refine_prompt
from langgraph.prebuilt.tool_node import ToolNode
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.tools import Tool
from state_data_classes import DeepAgentState, ReACTResponse, FinalDesign, DesignReview
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub


class DeepAgent:

    def __init__(self, llm_client, user_prompt: str, tools: List[ToolNode]=[]):
        
        self.llm = llm_client
        self.user_prompt = user_prompt
        self.messages = []
        self.tool_llm = None
        self.counter = 0
        
        google_serper = GoogleSerperAPIWrapper()
        self.search_tool = Tool(
            name="google_search", 
            func=google_serper.run,
            description="Search the web for relevant information",)
        
        self.tools = [self.search_tool]


    def execute(self, state: DeepAgentState):
        print(f"\n\n Planning...")
      
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

        #print(f"\n execute results :: {result}\n")
        self.messages.append(AIMessage(content=str(result)))
        return {"results": result}


    def run_tools(self, state: DeepAgentState):
        print(f"\n\n running tools...")
        tool_messages = []
        for action in state["results"].action_list:
            print(f"\n\n-- running {action.action_name} {action.args}\n\n")
            tool = next((tool for tool in self.tools if tool.name == action.action_name), None)
            if tool:
                tool_output = tool.run(action.args)
                #print(f"\n\nTool Response: {observation}\n\n")
                tool_messages.append({"action": action.args, "observation":tool_output})
                time.sleep(3)
        return {"tool_messages": tool_messages}


    def clarify_questions(self, state: DeepAgentState):
        print(f"\n\n asking questions...")
        qna_dict = [dict]
        for question in state["results"].clarifying_questions:
            answer = input(question)            
            if answer:
                qna_dict.append({"question": question, "answer": answer})
        return {"question_answers": qna_dict}


    def observe(self, state: DeepAgentState):
        print(f"\n\n observing the thoughts based on search results and clarifyign questions...")
        self.counter+=1

        for qna in state["question_answers"]:
            self.messages.append(HumanMessage(content=f"Q: {qna['question']} A: {qna['answer']}"))

        for item in state["tool_messages"]:
            self.messages.append(HumanMessage(content=f"Action: {item['action']} Observation: {item['observation']}"))
        
        
        llm = self.tool_llm.with_structured_output(ReACTResponse)

        response = llm.invoke(self.messages)

        #print(f"\n\nObservation Response: {response}\n\n")
        self.messages.append(AIMessage(content=str(response)))
        return {"results": response}


    def final_response(self, state: DeepAgentState):
        print(f"\n\n generating final response....")
                
        llm = self.llm.with_structured_output(FinalDesign)

        if state.get("design_review"):
            self.messages.append(HumanMessage(content=f"Design Review Comments: {state['design_review'].review_comments}"))

        response = llm.invoke(self.messages)
        #print("\n=================================================================================================\n")
        #print(f"\n\nFinal Response: {response}\n\n")
        self.messages.append(AIMessage(content=str(response)))
        return {"final_design": response}


    def review(self, state: DeepAgentState):
        print(f"\n\n reviewing final response....")

        messages = [
                SystemMessage(content=review_prompt),
                ("placeholder", "{messages}"),
            ]
        
        prompt_template = ChatPromptTemplate.from_messages(messages)
       
        prompt_llm = prompt_template | self.llm.with_structured_output(DesignReview)

        result = prompt_llm.invoke({"messages": 
            [
                HumanMessage(str(state["final_design"]))
            ]
        })
                
        #print("\n=================================================================================================\n")
        #print(f"\n\nReview Response: {result}\n\n")
        self.messages.append(AIMessage(content=str(result)))
        return {"design_review": result}


    def refine(self, state: DeepAgentState):
        print(f"\n\n refining final response....")

        messages = [
                SystemMessage(content=refine_prompt),
                ("placeholder", "{messages}"),
            ]
        
        prompt_template = ChatPromptTemplate.from_messages(messages)
       
        prompt_llm = prompt_template | self.llm.with_structured_output(FinalDesign)

        result = prompt_llm.invoke({"messages": 
            [
                HumanMessage(state["input"]), 
                HumanMessage(str(state["final_design"])),
                HumanMessage(str(state["design_review"]))
            ]
        })
                
        #print("\n=================================================================================================\n")
        #print(f"\n\nRefined Final Design: {result}\n\n")
        self.messages.append(AIMessage(content=str(result)))
        return {"final_design": result}


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
        print(f"\n\n writng to file:: {filename} ")

        md_content = f"""
# {final_design.project_short_name}

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
        return "clarify_questions"

    def build_graph(self):
        graph = StateGraph(DeepAgentState)
        graph.add_node("execute", self.execute)
        #graph.add_node("solve_sub_problems", self.solve_sub_problems)
        graph.add_node("run_tools", self.run_tools)
        graph.add_node("clarify_questions", self.clarify_questions)
        graph.add_node("observe", self.observe)
        graph.add_node("final_response", self.final_response)
        graph.add_node("review", self.review)
        graph.add_node("final_response_post_review", self.refine)
        graph.add_node("write_final_design_to_markdown", self.write_final_design_to_markdown)

        graph.add_edge(START, "execute")
        graph.add_edge("execute", "clarify_questions")
        #graph.add_edge("solve_sub_problems", "clarify_questions")
        graph.add_edge("clarify_questions", "run_tools")
        graph.add_edge("run_tools", "observe")

        graph.add_conditional_edges("observe", self.should_continue, 
                {
                    "final_response": "final_response",
                    "clarify_questions": "clarify_questions",                    
                })
        graph.add_edge("final_response", "review")
        graph.add_edge("review", "final_response_post_review")
        graph.add_edge("final_response_post_review", "write_final_design_to_markdown")

        app = graph.compile()
        app.get_graph().print_ascii()
        return app

    
# Example usage after agent run:
def run():
    load_dotenv(override=True)
    
    llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model=os.getenv("OPENAI_MODEL"))
    
    agent = DeepAgent(llm, None, None)    
    app = agent.build_graph()

    config = {"recursion_limit": 30}

    #user_input = "Build a copilot agent that can help developers write, debug, execute code faster and uses OSS LLMs"
    #user_input = "Build a chat bot that can answer questions about the stock market"
    #user_input = "Improve RAG perforamance for document search and question answering"
    #user_input = "Coding agent that can write, debug and explain code"
    #user_input = "prompt generator with self improvement"
    #user_input = "Build a ai solution architect agent that can create solution architecture design documents for a given software problem statement"
    #user_input = "Build data mesh"
    user_input = "build agentic RAG system"
    
    inputs = {"input": user_input }    
    app.invoke(input=inputs, config=config)

if __name__ == "__main__":
    run()