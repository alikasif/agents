import dspy
from dotenv import load_dotenv
from dspy.datasets import MATH
from typing import Literal
from langchain_community.utilities import GoogleSerperAPIWrapper


load_dotenv(override=True)

gpt4o_mini = dspy.LM('openai/gpt-4o-mini', max_tokens=2000)
dspy.configure(lm=gpt4o_mini)  # we'll use gpt-4o-mini as the default LM, unless otherwise specified
dspy.settings.configure(track_usage=True)


def calculator(expression: str) -> str:
    """Evaluate a mathematical expression."""
    try:
        result = eval(expression)  # Note: Use safely in production
        return f"The result is {result}"
    except:
        return "Invalid expression"

def google_search(query: str):
    print(f"\nsearcing google with query {query}")
    search = GoogleSerperAPIWrapper()
    return search.run(query)

# Define your tools as functions
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    # In a real implementation, this would call a weather API
    return f"The weather in {city} is sunny and 75°F"


def react_tool():
    # Create a ReAct agent
    react_agent = dspy.ReAct(
        signature="question -> answer",
        tools=[get_weather, google_search],
        max_iters=5
    )

    # Use the agent
    result = react_agent(question="What's the weather like in Tokyo?")
    print(result.answer)
    print("Tool calls made:", result.trajectory)


class ToolSignature(dspy.Signature):
    """Signature for manual tool handling."""
    question: str = dspy.InputField()
    tools: list[dspy.Tool] = dspy.InputField()
    outputs: str = dspy.OutputField()


# Create tool instances
tools = {
    "weather": dspy.Tool(get_weather),
    "calculator": dspy.Tool(calculator),
    "google_search": dspy.Tool(google_search)
}


# Create predictor
predictor = dspy.Predict(signature=ToolSignature)


# # Make a prediction
# response = predictor(
#     question="What's the weather in New York?",
#     tools=list(tools.values())
# )

# print(response)

# # Execute the tool calls
# for call in response.outputs.tool_calls:
#     # Execute the tool call
#     result = call.execute()
#     # For versions earlier than 3.0.4b2, use: result = tools[call.name](**call.args)
#     print(f"Tool: {call.name}")
#     print(f"Args: {call.args}")
#     print(f"Result: {result}")

