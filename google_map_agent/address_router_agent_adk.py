
"""
address router agent takes 2 addresses image. 
It call address extractor agent to extract the address from images.
It then call google map apis to extract the latitude and longitude of the addresses and finally route api to show the route between the addresses.

Address extractor agent is a sub agent and google apis are the tools.

Both the agents, main & sub agent uses Local LLM to generate the response.
"""

from google.adk.agents import LlmAgent, BaseAgent, SequentialAgent
from google.genai import types
from google.adk.models.lite_llm import LiteLlm
import os
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
import asyncio
from google.adk.sessions import Session
from google_map_apis import get_gmap_address, compute_route, create_google_maps_route_link
from data_classes import Route, Address
from prompts import router_agent_prompt

load_dotenv(override=True)


source_image_path = "google_map_agent//origin.jpg"
# read .jpg file bytes
with open(source_image_path, "rb") as f:
    source_image_bytes = f.read()

source_image_part = types.Part.from_bytes(
    data=source_image_bytes,
    mime_type="image/jpeg",
)

destination_image_path = "google_map_agent//destination.jpg"
# read .jpg file bytes
with open(destination_image_path, "rb") as f:
    destination_image_bytes = f.read()

destination_image_part = types.Part.from_bytes(
    data=destination_image_bytes,
    mime_type="image/jpeg",
)


llm = LiteLlm(
    model=f"openai/{os.getenv('OLLAMA_MODEL')}",
    api_base=os.getenv('OLLAMA_API_BASE')
)

#llm = model=os.getenv('GOOGLE_MODEL')

# Create an LLM Agent, providing instructions and the local model instance
image_to_text_agent = LlmAgent(
    name="TextExtractorAgent",
    description="Extract text from an image.",
    instruction="You will be given 2 images. Extract the text from the images. \
    example output: \n \n origin_address = 1600 Amphitheatre Parkway, Mountain View, CA \n destination_address = 1 Infinite Loop, Cupertino, CA",        
    model=llm,    
)


text_to_address_agent = LlmAgent(
    name="AddressExtractorAgent",
    description="Get latitude and longitude from a address.",
    instruction="You will be given 2 addresses. You have access to the tool get_gmap_address. \
        Call the tool get_gmap_address by passing the address to get the latitude and longitude of the address. \
        return the response as latitude and longitude. \
        example output: \
            origin_lat = 37.422 \
            origin_lng = -122.084 \
            destination_lat = 37.338 \
            destination_lng = -122.06",  
    model=llm,
    tools=[
        get_gmap_address,
    ],
)


# Create an LLM Agent, providing instructions and the local model instance
route_agent = LlmAgent(
    name="RouteAgent",
    description="Get the route between two coordinates using Google Maps Directions API.",
    instruction=router_agent_prompt,
    model=llm,
    tools=[
        create_google_maps_route_link,
    ],
)


main_agent = SequentialAgent(
    name="AddressRouterAgent",
    description="Main Coordinator Agent",
    sub_agents=[image_to_text_agent, text_to_address_agent, route_agent],    
)

# Run the agent in memory
runner = InMemoryRunner(agent=main_agent, app_name="address_router_app")

# Use the runner's session service to create a session (not a separate one!)
example_session = asyncio.run(runner.session_service.create_session(
    app_name="address_router_app",
    user_id="local_user",     
))

content = types.Content(role='user', parts=[source_image_part, destination_image_part])
events = runner.run(user_id=example_session.user_id, session_id=example_session.id, new_message=content)

address = ""
for event in events:
    if event.content:
        #print(f"\nevent ==> {event.content}")
        address = event.content.parts[0].text

runner.close()
print(address)

