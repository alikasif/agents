"This file containes the Incident commander Agent built using Google ADK which is responsible for managing incident response and coordination."

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from python_a2a import A2AServer, Message, TextContent, MessageRole, run_server
from python_a2a import A2AClient, Message, TextContent, MessageRole
from dotenv import load_dotenv
import os
import asyncio


class IncidentCommanderAgent(A2AServer):
    """A simple agent that manages incident response and coordination."""

    def __init__(self, remote_agent_urls):
        agent_details = {
            "name": "IncidentCommanderAgent",
            "description": "Agent to manage incident response and coordination effectively.",
            "model": os.getenv("GOOGLE_MODEL", "gpt-4.1-mini"),
            "tools": []
        }
        
        self.remote_agent_info = []
        self.agent_dict = {}
        self.remote_agent_urls = remote_agent_urls
        self.create_agent_connection_dict()
        
        super().__init__(**agent_details)
        self.agent = self.get_agent(model=os.getenv("GOOGLE_MODEL"))


    def create_agent_connection_dict(self):
        """Create a dictionary to hold agent names and their corresponding A2AClient instances."""
        for url in self.remote_agent_urls:
            client = A2AClient(url)
            self.agent_dict[client.agent_card.name] = client      


    def list_remote_agents(self):
            """List the available remote agents you can use to delegate the task."""
            
            if not self.remote_agent_urls:
                return []

            for url in self.remote_agent_urls:
                client = A2AClient(url)
                self.remote_agent_info.append(
                    {'name': client.agent_card.name, 'description': client.agent_card.description}
                )
                #self.agent_dict[client.agent_card.name] = client      
            print(f"####Available agents: {self.remote_agent_info}")
            print(f"^^^^Agent dictionary: {self.agent_dict}")
            return self.remote_agent_info


    def send_message(self, agent_name: str, message: str):
            
        """Send a message to the specified agent and return the response."""

        print(f"available agents: {self.agent_dict}")
        if agent_name not in self.agent_dict:
            raise ValueError(f"Agent {agent_name} is not available.")
        
        client = self.agent_dict[agent_name]
        message = Message(
            content=TextContent(text=message),
            role=MessageRole.USER
        )
        response = client.send_message(message)
        Message( content=TextContent(text=f"{response}"),
                 role=MessageRole.AGENT,
                 parent_message_id=message.message_id,
                 conversation_id=message.conversation_id
                )
        print(f"*****Response from***** {agent_name}: {response}")
        return response


    def get_agent(self, model: str):

        return LlmAgent(
            name= "IncidentCommanderAgent",
            description= "Agent to manage incident response and coordination effectively.",
            instruction= """You are an incident commander agent. Your job is to manage incident response and coordination effectively.
                        You will be provided with incident chat on from an incident slack channel.
                        You will be responsible for coordinating with different agents to get the triage done, send out communications and prepare a post mortem report to ensure a smooth incident response process.
                        You must look at all the agents available to you and use the agent name to delegate the task. You must also pass on the response received form other agents to the next agent.
                        Finally you must respond with the incident post-mortem report and stake holder email that you would send to the stakeholders.""",
            model=model,
            tools=[self.list_remote_agents, self.send_message]
        )
    
    
    def handle_message(self, message: str):
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
    

    def get_runner(self, user_id, session_id):

        # Set up runner and session for execution
        APP_NAME = "incident_commander_app"
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
    urls = [
        "http://localhost:5004/a2a",  # Incident Triage Agent
        "http://localhost:5002/a2a",  # Incident Comms Agent
        "http://localhost:5003/a2a"   # Incident Post Mortem Agent
    ]


    # chat = read_incident_chat_file("agent_comms/incidents_transcript/incident_1.txt")
    # response=IncidentCommanderAgent(urls).run_agent(chat)
    # print(f"Agent says: {response}")


    run_server(IncidentCommanderAgent(urls), host="0.0.0.0", port=5000)
    # This will start the A2A server and listen for incoming messages.