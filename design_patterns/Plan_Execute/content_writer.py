from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
import operator
from typing import Annotated, List, Tuple
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from typing import Union
from typing import Literal
from langgraph.graph import END
from langgraph.graph import StateGraph, START
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from prompt import blog_prompt, linkedin_prompt
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv(override=True)
class PlanExecute(TypedDict):
    input: str
    plan: List[str]
    past_steps: Annotated[List[Tuple], operator.add]
    response: str

class Plan(BaseModel):
    """Plan to follow in future"""

    steps: List[str] = Field(
        description="different steps to follow, should be in sorted order"
    )

class Response(BaseModel):
    """Response to user."""
    response: str

class Act(BaseModel):
    """Action to perform."""
    action: Union[Response, Plan] = Field(
        description="Action to perform. If you want to respond to user, use Response. "
        "If you need to further use tools to get the answer, use Plan."
    )


tools = [TavilySearchResults(max_results=5)]
llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model=os.getenv("OPENAI_MODEL"))

# llm = ChatGoogleGenerativeAI(
#     model=os.getenv("GOOGLE_MODEL"),
#     temperature=0,
#     max_retries=2,
# )

prompt = "You are a helpful assistant."
agent_executor = create_react_agent(llm, tools, prompt=prompt)


planner_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """For the given objective, come up with a simple 5 step plan. \
                This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps. \
                The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.
                Use Action to run one of the actions available to you - then return PAUSE.                
                """,
        ),
        ("placeholder", "{messages}"),
    ]
)
planner = planner_prompt | llm.with_structured_output(Plan)

def plan_step(state: PlanExecute):
    plan = planner.invoke({"messages": [("user", state["input"])]})
    print(f"plan steps::\n\n {plan.steps}")
    return {"plan": plan.steps}


def execute_step(state: PlanExecute):
    #print(f"\n\nPlanExecute step {state}")

    plan = state["plan"]
    plan_str = "\n".join(f"{i + 1}. {step}" for i, step in enumerate(plan))
    task = plan[0]
    task_formatted = f"""For the following plan: {plan_str}\n\nYou are tasked with executing step {1}, {task}."""
    
    agent_response = agent_executor.invoke(
        {"messages": [("user", task_formatted)]}
    )
    
    return {
        "past_steps": [(task, agent_response["messages"][-1].content)],
    }


replanner_prompt = ChatPromptTemplate.from_template(
    """
        For the given objective, come up with a simple step by step plan. \
        This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps. \
        The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.

        Your objective was this:
        {input}

        Your original plan was this:
        {plan}

        You have currently done the follow steps:
        {past_steps}

        Update your plan accordingly. If no more steps are needed and you can return to the user, then respond with that. 
        Otherwise, fill out the plan. Only add steps to the plan that still NEED to be done. Do not return previously done steps as part of the plan.
    """
)
replanner = replanner_prompt | llm.with_structured_output(Act)

def replan_step(state: PlanExecute):
    output = replanner.invoke(state)

    if isinstance(output.action, Response):
        return {"response": output.action.response}
    else:
        return {"plan": output.action.steps}


def should_end(state: PlanExecute):
    if "response" in state and state["response"]:
        return END
    else:
        return "agent"


workflow = StateGraph(PlanExecute)

# Add the plan node
workflow.add_node("planner", plan_step)

# Add the execution step
workflow.add_node("agent", execute_step)

# # Add a replan node
workflow.add_node("replan", replan_step)

workflow.add_edge(START, "planner")

# # From plan we go to agent
workflow.add_edge("planner", "agent")

# # From agent, we replan
workflow.add_edge("agent", "replan")

workflow.add_conditional_edges(
    "replan",
    # Next, we pass in the function that will determine which node is called next.
    should_end,
    ["agent", END],
)

app = workflow.compile()

try:    
    app.get_graph().print_ascii()
except Exception as e:
    print(str(e))

config = {"recursion_limit": 50}
# inputs = {"input": "Write a blog about Agentic AI Design Patterns. It is important to understand these patterns to build the domain specific agents."
#           "AI design patterns are not built in silo but are rather the combination of other pattenrs to come up with newer pattern."
#           "Specifically about patterns like Reflection, Tool(ReACT & ReWoo) and Planning which are used to build deep reasearch agents, and solve complex problems using step by step plan like Humans."}

inputs = {"input": blog_prompt }
response = app.invoke(input=inputs, config=config)
print(f"\n\n response: \n\n {response}")
