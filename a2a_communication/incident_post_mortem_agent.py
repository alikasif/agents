"This file containes the Incident Post moretem Agent built using Autogen which is responsible for managing post-incident reviews and documentation."

from autogen_agentchat.agents import AssistantAgent
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.messages import TextMessage
from python_a2a import A2AServer, Message, TextContent, MessageRole, run_server
from python_a2a import A2AClient, Message, TextContent, MessageRole
import asyncio
from dotenv import load_dotenv
import os
from autogen_core.models import ModelFamily


class IncidentPostMortemAgent(A2AServer):
    """A simple agent that assists in creating a post-mortem report for incidents."""   

    def __init__(self):
        agent_details = {
            "name": "IncidentPostMortemAgent",
            "description": "Agent to assist in creating a post-mortem report for incidents.",
            "model": os.getenv("DEEPSEEK_MODEL", "gpt-4.1-mini"),
            "tools": []
        }

        super().__init__(**agent_details)

        custom_model_client = OpenAIChatCompletionClient(
            model= os.getenv("ANTHROPIC_MODEL"),
            base_url= os.getenv("ANTHROPIC_BASE_URL"),
            api_key= os.getenv("ANTHROPIC_API_KEY"),
            model_info={
                "vision": False,
                "function_calling": False,
                "json_output": False,
                "family": ModelFamily.R1,
                "structured_output": True,
            },
        )

        self.agent = self.get_agent(custom_model_client)
    
    def handle_message(self, message):
        if message.content.type == "text":
            # Here you would implement the logic to create a post-mortem report.
            response = asyncio.run(self.run_agent(message.content.text))
            return Message(
                    content=TextContent(text=f"Incident Triage Summary: {response}"),
                    role=MessageRole.AGENT,
                    parent_message_id=message.message_id,
                    conversation_id=message.conversation_id
                )
                

    def get_agent(self, model_client):

        return AssistantAgent(
            name="IncidentPostMortemAgent",
            model_client=model_client,
            system_message="You are an expert in managing post-incident reviews and documentation. " \
            "Your role is to assist in creating a comprehensive post-mortem report that includes the timeline of events, root cause analysis, and recommendations for future prevention." \
            "Your report of 500 words must include the following sections: " \
            "1. Some background of what this application is about and what it does. " \
            "2. Incident Overview: A brief description of the incident, including the date and time it occurred, and the systems affected. " \
            "3. Timeline of Events: A detailed timeline of events leading up to, during, and after the incident. " \
            "4. Root Cause Analysis: An analysis of the root cause of the incident, including any contributing factors. " \
            "5. Impact Assessment: An assessment of the impact of the incident on the organization, including any financial or reputational damage. " \
            "6. Mitigation Steps: A description of the steps taken to mitigate the incident and prevent it from happening again in the future. " \
            "7. Recommendations: A list of recommendations for future prevention, including any changes to processes or systems that should be made. " \
            "8. Conclusion: A summary of the incident and the steps taken to address it.",   
            model_client_stream=True
        )


    async def run_agent(self, query: str):
        # Create content from user query

        message = TextMessage(content=query, source="user")

        response = await self.agent.on_messages([message], cancellation_token=CancellationToken())
        return response.chat_message.content

def read_incident_chat_file(file_path):
    """Read the incident chat file and return its content."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


if __name__ == "__main__":

    load_dotenv(override=True)
    
    # chat = read_incident_chat_file("agent_comms/incidents_transcript/incident_1.txt")
    # triage = read_incident_chat_file("agent_comms/incidents_transcript/incident_1_triage.txt")    
    # chat_triage = f"incident Chat: {chat}\n\n" + f"incident Triage Chat: {triage}"
    # response = asyncio.run(IncidentPostMortemAgent().run_agent(chat_triage))
    # print(f"Agent says: {response}")

    run_server(IncidentPostMortemAgent(), host="0.0.0.0", port=5003)
    # This will start the A2A server and listen for incoming messages.