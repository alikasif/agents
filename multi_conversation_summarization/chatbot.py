
from dotenv import load_dotenv
import os
from agents import Agent, Runner, SQLiteSession
from agents.model_settings import ModelSettings
from prompts import *
import asyncio
from tools import google_search
from data_classes import ChatConversation

load_dotenv(override=True)

async def chat_session(session_id: str):

    chatbot_agent = Agent(
            name="Assistant",
            instructions=CHTABOT_PROMT,
            tools=[google_search],
            model_settings=ModelSettings(tool_choice="auto"),
            model=os.getenv("OPENAI_MODEL"),
    )

    session = SQLiteSession(session_id)

    while True:

        user_input = input("\n\nEnter your question (or 'exit' to quit): ").strip()
        
        if user_input.lower() == "exit":
            print("Exiting...")
            break

        if not user_input:
            print("Please enter a valid question.")
            continue

        result = await Runner.run(chatbot_agent, user_input,session=session)
        print(result.final_output)  # "San Francisco"
 

    print("\nFull conversation history: ")
    chats = []
    for conv in await session.get_items():   
        
        print(f"\nDEBUG: {conv}")        
        if not conv.get("role"):
            continue
        
        role = None
        tmp_conv = None

        if conv["role"] == "user":     
            print("\n",conv["role"], conv["content"])
            role = "User"
            tmp_conv = conv["content"]
        else:
            print("\n",conv["role"], conv["content"][0]["text"])
            role = "Assistant"
            tmp_conv = conv["content"][0]["text"]
        
        chats.append(ChatConversation(role=role, content=tmp_conv))
    
    all_conv = "\n".join([f"{chat.role}: {chat.content}" for chat in chats])
    return all_conv

async def summary_agent(conversation: str):

    print("Starting summarization agent...")

    agent = Agent(
            name="Assistant",
            instructions=CONVERSATION_SEGMENTATION_SYSTEM_PROMPT,
            model=os.getenv("OPENAI_MODEL"),
    )

    print("Summary agent is ready.\n")

    user_prompt = get_segmentation_prompt(conversation, 1, .8)
    result = await Runner.run(agent, user_prompt)
    print("summarization output:\n\n",result.final_output)


if __name__ == "__main__":
    #asyncio.run(conv_agent())
    all_conv = asyncio.run(chat_session("conversation_123"))
    asyncio.run(summary_agent(all_conv))


