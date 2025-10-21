
from prompts import *
from data_classes import *
import os
from dotenv import load_dotenv
import logging
import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END

logging.basicConfig(level=logging.INFO) # Set the root logger level to INFO


def get_model(prefix = "OPENAI"):        
        
        # if prefix == "OPENAI":
        #     return os.getenv(prefix+"_MODEL")
        
        # external_client = AsyncOpenAI(
        #     api_key=os.getenv(prefix+"_API_KEY"),
        #     base_url=os.getenv(prefix+"_BASE_URL")
        # )

        llm = init_chat_model(model=os.getenv(prefix+"_MODEL"), model_provider="openai")        
        return llm


def generate(state: OptimizerState):    
    
    llm = get_model()
    llm = llm.with_structured_output(GeneratorOutput)
    
    messages = []
    generator_prompt = state["generator_prompt"]
    generated_prompt = generator_prompt.format(topic=state["user_input"])    
    messages.append({"role":"system", "content": generated_prompt})    
    
    response = llm.invoke(messages)        

    print(f"\n generate: {response}")    
    
    return {"generator_output": response.linkedin_post}


def reflector(state: OptimizerState):

    improved_prompt = improve_prompt.format(USER_INPUT=state["user_input"], ORIGINAL_PROMPT=state["generator_prompt"], GENERATED_OUTPUT=state["generator_output"])
    print(f"\n\n improved prompt {improved_prompt}\n\n")

    messages = [{"role": "human", "content":improved_prompt}]
    llm = get_model("OPENAI_GPT5")
    response = llm.invoke(messages)
    
    print(f"\nreflector : {response.content}\n")    
    return {"reflector_json": response.content}


def optimizer(state: OptimizerState):
    optimized_prompt = optimizer_prompt.format(generator_prompt=state["generator_prompt"], REFLECTOR_JSON=state["reflector_json"])
    print(f"\n\n optimized_prompt {optimized_prompt}\n\n")

    messages = [{"role": "human", "content":optimized_prompt}]
    llm = get_model().with_structured_output(OptimizerOutput)
    response = llm.invoke(messages)
    
    print(f"\n\noptimizer : {response}\n")    

    return {"optimizer_output": response, "loop_count": state.get("loop_count", 0)+1}


def re_generate(state: OptimizerState):
        
    llm = get_model()    
    
    messages = []
    optimizer_output = state["optimizer_output"]

    print(f"\n\n prompt text :: {optimizer_output.prompt_text}")
    
    messages.append({"role":"system", "content": optimizer_output.prompt_text})    
    messages.append({"role":"user", "content": state["user_input"]})    
    
    response = llm.invoke(messages)        

    print(f"\n\n re_generate: {response.content}")    
    
    return {"re_generator_output": response.content}


def judge(state: OptimizerState):
        
    llm = get_model()    
    judged_prompt = judge_prompt.format(user_input=state["user_input"], original_output=state["generator_output"], regenerated_output=state["re_generator_output"])
    messages = []
    
    print(f"\n\n judged_prompt :: {judged_prompt}")
    
    messages.append({"role":"system", "content": judged_prompt})        
    
    response = llm.invoke(messages)        

    print(f"\n\n judge: {response.content}")    
    
    return {"judge": response.content}



def should_continue(state: OptimizerState):
     
    if state.get("loop_count", 0) > 3:
          return END
    return "generate"


def run():
    workflow = StateGraph(OptimizerState)

    workflow.add_node("generate", generate)
    workflow.add_node("reflector", reflector)
    workflow.add_node("optimizer", optimizer)
    workflow.add_node("re_generate", re_generate)
    workflow.add_node("judge", judge)

    workflow.add_edge(START, "generate")    
    workflow.add_edge("generate", "reflector")
    workflow.add_edge("reflector", "optimizer")
    workflow.add_edge("optimizer", "re_generate")
    workflow.add_edge("re_generate", "judge")

#    workflow.add_conditional_edges("optimizer", should_continue)

    app = workflow.compile()
    app.invoke({"generator_prompt": generator_prompt, "user_input": "Agent design patterns"})


if __name__ == "__main__":
     load_dotenv(override=True)
     run()

