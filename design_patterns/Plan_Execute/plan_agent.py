from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

load_dotenv(override=True)

llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"), 
    model=os.getenv("OPENAI_MODEL"),)        

# class LLMNode:
#     def __init__(self, llm):
#         self.llm = llm
#     def __call__(self, state):
#         # Implement your custom logic here
#         # Access the state and perform actions
#         messages = state["messages"]
#         response = self.llm.invoke(messages)
#         return {"messages": [response]}
# llm_node = LLMNode(llm)
    

class State(TypedDict):
    # messages have the type "list".
    # The add_messages function appends messages to the list, rather than overwriting them
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)


def chatbot(state: State):
    print(f"\n\nstate: {state}")
    return {"messages": [llm.invoke(state["messages"])]}
graph_builder.add_node("chatbot", chatbot)


graph_builder.set_entry_point("chatbot")
graph_builder.set_finish_point("chatbot")

#graph_builder.add_node("llm_node", llm_node)
# Set entry and finish points
# graph_builder.set_entry_point("llm_node")
# graph_builder.set_finish_point("llm_node")

graph = graph_builder.compile()
try:    
    graph.get_graph().print_ascii()
except Exception as e:
    print(str(e))


# Run the chatbot
while True:
    user_input = input("User: ")
    if user_input.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")
        break
    for event in graph.stream({"messages": HumanMessage( content=user_input)}):
    #for event in graph.stream({"messages": [("user", user_input)]}):
        for value in event.values():
            #print("Assistant:", value["messages"][-1].content)
            print(f"Assistant: {value["messages"]}")

