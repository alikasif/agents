
from prompts import *
from data_classes import *
import os
from dotenv import load_dotenv
import logging
import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END

from langgraph.prebuilt import create_react_agent

from langchain_community.llms import OpenAI
from tools import get_google_search_tool


logging.basicConfig(level=logging.INFO) # Set the root logger level to INFO


def get_model(prefix = "OPENAI", provider="openai"):        
       
    llm = init_chat_model(model=os.getenv(prefix+"_MODEL"), model_provider=provider)        
    return llm


def get_agent(prompt: str, modle_prefix="OPENAI", provider ="openai", response_format=None):    
    
    if response_format:
        return create_react_agent(model=get_model(prefix=modle_prefix, provider=provider), tools=[get_google_search_tool()], response_format=response_format)
    
    return create_react_agent(model=get_model(prefix=modle_prefix, provider=provider), tools=[get_google_search_tool()])


def generate(state: OptimizerState):    
    
    print(f"============================================================generate===========================================================================")
    
    llm = get_model()
    llm = llm.with_structured_output(GeneratorOutput)
    
    messages = []
    generator_prompt = state["generator_prompt"]
    generated_prompt = generator_prompt.format(topic=state["user_input"])    
    messages.append({"role":"system", "content": generated_prompt})    
    
    response = llm.invoke(messages)        

    print(f"\n**generate: {response}")
    
    
    return {"generator_output": response.linkedin_post}


def agentic_reflector(state: OptimizerState):
    print(f"======================================================agentic_reflector {state["loop_count"]}=====================================================================")
    user_input = state["user_input"]
    generator_prompt = state["generator_prompt"]
    generator_prompt = generator_prompt.format(topic=user_input)

    improved_prompt = prompt_reviewer.format(USER_INPUT=user_input, 
                                             ORIGINAL_PROMPT=generator_prompt, 
                                             GENERATED_OUTPUT=state["generator_output"])
    
    #print(f"\n\n improved prompt {improved_prompt}\n\n")

    messages = [{"role": "human", "content":improved_prompt}]
    agent = get_agent("OPENAI_GPT5", response_format=AgenticReflectorOutput)

    response = agent.invoke({"messages": messages})
    
    print(f"\n**reflector : {response["structured_response"]}\n")    
    
    return {"reflector_json": response["structured_response"], "loop_count": state.get("loop_count", 0)+1}



def agentic_optimizer(state: OptimizerState):
    
    print(f"========================================================agentic_optimizer {state["loop_count"]}=======================================================================")

    optimized_prompt = optimizer_prompt.format(generator_prompt=state["generator_prompt"], 
                                               REFLECTOR_JSON=state["reflector_json"], 
                                               USER_INPUT=state["user_input"])

    #print(f"\n\n optimized_prompt {optimized_prompt}\n\n")

    messages = [{"role": "human", "content":optimized_prompt}]
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
    workflow.add_edge("agentic_reflector", "optimizer")
    workflow.add_edge("optimizer", "re_generate")
    workflow.add_conditional_edges("re_generate", should_continue)

    app = workflow.compile()
    
    app.invoke({"generator_prompt": generator_prompt, 
                "user_input": "feature bloating and code bloating due to the use of co-pilot", 
                "loop_count":0})


if __name__ == "__main__":
     load_dotenv(override=True)
     run()

