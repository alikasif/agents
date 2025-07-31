from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
import yaml
from typing import Dict, Any
from autogen_core import CancellationToken
from autogen_agentchat.messages import TextMessage


def read_yaml_spec(yaml_file: str) -> str:
    """
    Reads and returns OpenAPI spec from YAML file
    """
    try:
        with open(yaml_file, 'r') as f:
            yaml_dict = yaml.safe_load(f)
            return yaml.dump(yaml_dict, sort_keys=False)
    except Exception as e:
        return f"Error reading YAML file: {str(e)}"


def create_agent() -> AssistantAgent:
    """
    Creates an AutoGen AssistantAgent for API endpoint selection
    """
    
    model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")

    # Create the assistant agent
    agent = AssistantAgent(
        name="api_endpoint_assistant",
        model_client=model_client,
        system_message="""You are an API endpoint selection expert. 
        Use the read_yaml_spec tool to read the OpenAPI specification, then return 
        ONLY the appropriate REST endpoint (method, path and arguments) for user queries.""",
        model_client_stream=True,
        tools=[read_yaml_spec],
        reflect_on_tool_use=True
    )
    
    return agent

async def execute_user_query(user_input: str):
    """
    Executes a user query using the API endpoint assistant agent
    """
    agent = create_agent()
    user_message = TextMessage(content=user_input, source="user")
    yaml_path = TextMessage(content="D:\GitHub\agents\api_chatbot\dog_store.yaml", source="user")
    
    response = await agent.on_messages([user_message, yaml_path], cancellation_token=CancellationToken())
    # for inner_message in response.inner_messages:
    #     print(inner_message.content)
    return response.chat_message.content

    