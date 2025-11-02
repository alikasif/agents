
from prompts import *
from data_classes import *
import os
from dotenv import load_dotenv
import logging
import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START

from langgraph.prebuilt import create_react_agent

from tools import get_google_search_tool



logging.basicConfig(level=logging.INFO) # Set the root logger level to INFO


def get_model(prefix = "OPENAI", provider="openai"):        
       
    llm = init_chat_model(model=os.getenv(prefix+"_MODEL"), model_provider=provider)        
    return llm


def get_agent(modle_prefix="OPENAI", provider ="openai", response_format=None):    
    
    if response_format:
        return create_react_agent(model=get_model(prefix=modle_prefix, provider=provider), tools=[get_google_search_tool()], response_format=response_format)
    
    return create_react_agent(model=get_model(prefix=modle_prefix, provider=provider), tools=[get_google_search_tool()])


def generate(state: OptimizerState):    
    
    print(f"============================================================generate===========================================================================")
    
    formatted_prompt = reasoning_trajectory_prompt.format(user_query= state["user_input"], 
                                       list_of_current_bullets_with_ids_and_content= "google_search_tool: useful for searching recent information")

    agent = get_agent(response_format=GeneratorOutput)    
    
    messages = []
    
    messages.append({"role":"system", "content": formatted_prompt})        
    
    response = agent.invoke({"messages": messages})

    print(f"\n**generate: {response["structured_response"]}")
    
    return {"generator_output": response["structured_response"]}


def agentic_reflector(state: OptimizerState):
    print(f"======================================================agentic_reflector {state["loop_count"]}=====================================================================")
    
    reasoning_trajectories = state["generator_output"]
    formatted_prompt = reflector_prompt.format(reasoning_trace=reasoning_trajectories)
   
    messages = [{"role": "human", "content":formatted_prompt}]
    agent = get_agent("OPENAI_GPT5", response_format=AgenticReflectorOutput)

    response = agent.invoke({"messages": messages})
    
    print(f"\n**reflector : {response["structured_response"]}\n")    

    deltas = "\n".join(response["structured_response"].proposed_deltas)
    
    return {"reflector_json": deltas, "loop_count": state.get("loop_count", 0)+1}


def agentic_optimizer(state: OptimizerState):
    
    print(f"========================================================agentic_optimizer {state["loop_count"]}=======================================================================")

    formatted_prompt = curator_prompt.format(proposed_deltas=state["reflector_json"])

    #print(f"\n\n optimized_prompt {optimized_prompt}\n\n")

    messages = [{"role": "human", "content":formatted_prompt}]
    
    agent = get_agent("OPENAI_GPT5", response_format=OptimizerOutput)
    
    response = agent.invoke({"messages": messages})

    prompt = response["structured_response"].prompt_text
    user_input = response["structured_response"].user_input
    
    print(f"\n\n**optimizer \n\n improved prompt: {response["structured_response"]} ")    
    
    return {"user_input": user_input, "generator_prompt": prompt}


def re_generate(state: OptimizerState):
    
    print(f"======================================================== re_generate {state["loop_count"]}======================================================================")
        
    llm = get_model()    
    
    messages = []
    
    prompt = state["generator_prompt"]
    user_input = state["user_input"]

    #print(f"\n\n prompt text :: {optimizer_output.prompt_text}")
    
    messages.append({"role":"system", "content": prompt})    
    messages.append({"role":"user", "content": user_input})    
    
    response = llm.invoke(messages)        

    print(f"\n\n**re_generate: {response.content}")    
    
    return {"re_generator_output": state["generator_output"], "generator_output": response.content}


def judge(state: OptimizerState):
    print(f"========================================================judge {state["loop_count"]}============================================================================")    
    llm = get_model("GEMINI", "google_genai")    
    judged_prompt = judge_prompt.format(user_input=state["user_input"], original_output=state["generator_output"], regenerated_output=state["re_generator_output"])
    messages = []
    
    #print(f"\n\n judged_prompt :: {judged_prompt}")
    
    messages.append({"role":"system", "content": judged_prompt})        
    
    response = llm.invoke(judged_prompt)        

    print(f"\n\n**judge: {response.content}")
    
    return {"judge": response.content}


def should_continue(state: OptimizerState):
     
    if state.get("loop_count", 0) > 2:
          return "judge"
    return "agentic_reflector"


def run():
    workflow = StateGraph(OptimizerState)

    workflow.add_node("generate", generate)    
    workflow.add_node("agentic_reflector", agentic_reflector)
    workflow.add_node("optimizer", agentic_optimizer)
    workflow.add_node("re_generate", re_generate)
    workflow.add_node("judge", judge)

    workflow.add_edge(START, "generate")    

    workflow.add_edge("generate", "agentic_reflector")
    # workflow.add_edge("agentic_reflector", "optimizer")
    # workflow.add_edge("optimizer", "re_generate")
    # workflow.add_conditional_edges("re_generate", should_continue)

    app = workflow.compile()
    
    app.invoke({"loop_count": 0, "user_input": "Who won the 2016 Russian national silver medal with another Russian ice dancer born 29 April 1995?"})


if __name__ == "__main__":
     load_dotenv(override=True)
     run()

