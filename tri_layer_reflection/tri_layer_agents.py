from langchain.agents import create_agent
from dotenv import load_dotenv
from prompts import generator_prompt, thought_introspector_prompt, reflection_prompt, prompt_ranking_prompt
from tools import google_search
from data_classes import GeneratorOutput, ThoughtIntrospectorOutput, ReflectionOutput
import os
from langgraph.checkpoint.memory import InMemorySaver  

load_dotenv(override=True)

generator_agent = create_agent(
    model = os.getenv("ANTHROPIC_CHAT_MODEL_ID"),
    tools=[google_search],
    system_prompt=generator_prompt,
    response_format=GeneratorOutput
)

result = generator_agent.invoke(
    {"messages": [{"role": "user", "content": "write a linkedin post about LLM inference"}]}
)

print("Generator Agent Output:", result["structured_response"], "\n\n")

response = result["structured_response"]

thought_introspector_agent = create_agent(
    model = os.getenv("ANTHROPIC_CHAT_MODEL_ID"),
    tools=[google_search],
    system_prompt=thought_introspector_prompt,
    response_format=ThoughtIntrospectorOutput
)

result = thought_introspector_agent.invoke(
    {"messages": [{"role": "user", "content": f" generator_prompt: {generator_prompt}\n \
        user_input: write a linkedin post about LLM inference\n \
        generator_thought_trace: {response.thought_trace}\n \
        generator_final_answer: {response.final_answer}"}]}
)

print("Thought Introspector Agent Output:", result["structured_response"], "\n\n")

response2 = result["structured_response"]

reflection_agent = create_agent(
    model = os.getenv("ANTHROPIC_CHAT_MODEL_ID"),
    tools=[google_search],
    system_prompt=reflection_prompt,
    response_format=ReflectionOutput
)

result = reflection_agent.invoke(
    {"messages": [{"role": "user", "content": 
        f"generator_prompt: {generator_prompt}\n \
        user_input: write a linkedin post about LLM inference \n \
        generator_thought_trace: {response.thought_trace}\n \
        generator_final_answer: {response.final_answer}\n \
        cognitive_critique: {response2.cognitive_critique}\n \""
    }]}
)

print("Reflection Agent Output:", result["structured_response"], "\n\n")

response3 = result["structured_response"]

generator_agent = create_agent(
    model = os.getenv("ANTHROPIC_CHAT_MODEL_ID"),
    tools=[google_search],
    system_prompt=response3.improved_prompt,
    response_format=GeneratorOutput
)

result = generator_agent.invoke(
    {"messages": [{"role": "user", "content": "write a linkedin post about LLM inference"}]}
)

print("\nGenerator2 Agent Output:", result["structured_response"], "\n\n")

response4 = result["structured_response"]

judgement_agent = create_agent(
    model = os.getenv("ANTHROPIC_CHAT_MODEL_ID"),
    tools=[google_search],
    system_prompt=prompt_ranking_prompt,
)

result = judgement_agent.invoke(
    {"messages": [{"role": "user", "content": 
        f"generator_prompt: {generator_prompt}\n \
        user_input: write a linkedin post about LLM inference \n \
        generator_answer: {response.final_answer}\n \
        reflection_prompt: {response3.improved_prompt}\n \
        reflection_answer: {response4.final_answer}\n \""
    }]}
)

print("\nJudgement Agent Output:", result, "\n\n")

