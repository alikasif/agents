from dotenv import load_dotenv
import os
from agents import Agent, Runner, SQLiteSession
from agents.model_settings import ModelSettings
from prompts import *
import asyncio
from tools import google_search

load_dotenv(override=True)

print("Test script running")

async def test_chat_session():
    print("Starting test chat session...")
    print("Test chat session ended.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_chat_session())