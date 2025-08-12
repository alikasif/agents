from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from python_a2a import A2AServer, Message, TextContent, MessageRole, run_server
from python_a2a import Message, TextContent, MessageRole
from dotenv import load_dotenv
import os
import asyncio

"This file contains the Incident Comms Agent built using Google ADK which is responsible for managing communication during incidents."

class IncidentCommsAgent(A2AServer):
    """A simple agent that manages communication during incidents."""
    
    def __init__(self):
        agent_details = {
            "name": "IncidentCommsAgent",
            "description": "Your job is to manage the communication to various stakeholders during the incident. ",
            "model": os.getenv("GOOGLE_MODEL", "gpt-4.1-mini"),
            "tools": []
        }

        super().__init__(**agent_details)
        self.agent = self.get_agent(model=os.getenv("GOOGLE_MODEL"))


    def handle_message(self, message):
            
            if message.content.type == "text":
            # Here you would implement the logic to manage incident response and coordination.
                response = self.run_agent(message.content.text)
                print(f"Response from agent: {response}")    
                return Message(
                        content=TextContent(text=f"Incident Communication Summary: {response}"),
                        role=MessageRole.AGENT,
                        parent_message_id=message.message_id,
                        conversation_id=message.conversation_id
                    )


    def get_agent(self, model: str):

        return LlmAgent(
            name="IncidentCommsAgent",
            description="Agent to manage the communication to various stakeholders during the incident",
            instruction= """Your job is to manage the communication to various stakeholders durng the incident.
                            You must listen to the incident commander and be prepared to 
                            provide updates to the affected users, and ensure that all communication is clear and concise.
                            You will also be responsible for drafting messages to send out using email tool.
                            You must respond with only the final email message that you would send to the stakeholders.
                            """,
            model=model
        )


    def get_runner(self, user_id, session_id):

        # Set up runner and session for execution
        APP_NAME = "incident_comms_app"
        USER_ID = user_id
        SESSION_ID = session_id
        
        # Create session service and session
        session_service = InMemorySessionService()
        asyncio.run(session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID
        ))

        # Create runner
        runner = Runner(
            agent=self.agent,
            app_name=APP_NAME,
            session_service=session_service
        )
        return runner


    def run_agent(self, query: str):
        # Create content from user query
        content = types.Content(
            role="user",
            parts=[types.Part(text=query)]
        )
        USER_ID="kasif"
        SESSION_ID="incident_session_123"

        # Get the runner with user and session details
        runner = self.get_runner(user_id=USER_ID, session_id=SESSION_ID)        
        
        events = runner.run(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=content
        )
        
        # Process events to get the final response
        for event in events:
            if event.is_final_response():
                return event.content.parts[0].text
        return "No response received."

def read_incident_chat_file(file_path):
    """Read the incident chat file and return its content."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


if __name__ == "__main__":
    load_dotenv(override=True)
    
    # chat = read_incident_chat_file("agent_comms/incidents_transcript/incident_1_triage.txt")    
    # response= IncidentCommsAgent().run_agent(chat)
    # print(f"Agent says: {response}")

    run_server(IncidentCommsAgent(), host="0.0.0.0", port=5002)
    # This will start the A2A server and listen for incoming messages.