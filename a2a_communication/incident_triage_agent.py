from agents import Agent, ModelSettings, function_tool
from agents import Agent, Runner
from python_a2a import A2AServer, Message, TextContent, MessageRole, run_server
from python_a2a import A2AClient, Message, TextContent, MessageRole
from dotenv import load_dotenv
import os
import asyncio

"This file contains the Incident Triage Agent built using Open AI Agent SDK which is responsible for analyzing incident chats and preparing summaries of events as they happen."

class IncidentTriageAgent(A2AServer):
    """A simple agent that analyzes incident chats and prepares summaries of events."""


    def __init__(self):
        agent_details = {
            "name": "IncidentTriageAgent",
            "description": "Your job is to analyze the incident chats and prepare a summary of events as they happen. You must try to understand what went wrong, when it was reported, how it was reported, who reported it, time to triage, blast radius, mitigation steps, verification and resolution steps. Your job is to capture the information in a structured format and provide it to the incident commander.",
            "model": os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            "tools": []
        }
        super().__init__(**agent_details)
        self.agent = self.get_agent(model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"))

    def get_agent(self, model: str):

        return Agent(
            name="IncidentTriageAgent",
            instructions="Your job is to analyzes the chats during an incident and prepares a summary of events as it happens. " \
            "You must try to understand the what went wrong, when it was reported, how it was reported, who reported it, time to triage, blast radius, mitigation steps, verification and resolution steps." \
            "Your job is to capture the information in a structured format and provide it to the incident commander.",
            model=model,
            model_settings=ModelSettings(
                temperature=0.0,
            )
        )


    def handle_message(self, message):
        if message.content.type == "text":
            # Here you would implement the logic to analyze the incident chat
            # and prepare a summary of events.
            #print(f"Received message: {message.content.text}")
            response = self.run_agent(message.content.text)
            print(f"Response from agent: {response}")
            return Message(
                content=TextContent(text=f"Incident Triage Summary: {response}"),
                role=MessageRole.AGENT,
                parent_message_id=message.message_id,
                conversation_id=message.conversation_id
            )
    
    def run_agent(self, query: str):
        # Create content from user query
        content = {
            "role": "user",
            "parts": [{"text": query}]
        }
        result = asyncio.run(Runner.run(self.agent, query))
        #print(f"Agent response: {str(result)}")
        return result.final_output

def read_incident_chat_file(file_path):
    """Read the incident chat file and return its content."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

if __name__ == "__main__":
    load_dotenv(override=True)
    
    # chat = read_incident_chat_file("agent_comms/incidents_transcript/incident_1.txt")
    # response=IncidentTriageAgent().run_agent(chat)
    # print(f"Agent says: {response}")

    run_server(IncidentTriageAgent(), host="0.0.0.0", port=5004)
    # This will start the A2A server and listen for incoming messages.