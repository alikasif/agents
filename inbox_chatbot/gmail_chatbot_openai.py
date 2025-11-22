import asyncio
from dotenv import load_dotenv
import os
from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp
from agents.model_settings import ModelSettings
from datetime import timedelta
from prompts import get_system_prompt, get_browser_prompt, get_url_extraction_prompt
from tools import web_fetch
from data_classes import GmailToolResponse, GmailURLResponse

load_dotenv(override=True)

async def main() -> None:
    
    params = {"url": "http://localhost:8181/mcp", "timeout": timedelta(seconds=300), "sse_read_timeout": timedelta(seconds=600)}

    browser_agent = Agent(
                name="Assistant",
                instructions=get_browser_prompt(),
                tools=[web_fetch],
                model_settings=ModelSettings(tool_choice="required"),
                model=os.getenv("OPENAI_MODEL"),
    )

    url_extractor_agent = Agent(
                name="Assistant",
                instructions=get_url_extraction_prompt(),
                output_type=GmailURLResponse,
                model=os.getenv("OPENAI_MODEL"),

    )

    async with MCPServerStreamableHttp(
        name="Streamable HTTP Python Server",
        params=params,
        cache_tools_list=True,        
        client_session_timeout_seconds=600,
    ) as server:
        agent = Agent(
            name="Assistant",
            instructions=get_system_prompt(),
            mcp_servers=[server],
            #tools=[web_fetch],
            model_settings=ModelSettings(tool_choice="required"),
            output_type=GmailToolResponse,
            model=os.getenv("OPENAI_MODEL"),
        )

        while True:
            
            user_input = input("\n\nEnter your question (or 'exit' to quit): ").strip()
            if user_input.lower() == "exit":
                print("Exiting...")
                break
            if not user_input:
                print("Please enter a valid question.")
                continue
            
            print(f"\nrunning gmail agent")
            result = await Runner.run(agent, user_input)
            print(result)

            all_content = []
            for result in result.final_output.emails:
                all_content.append(result.messages)


            print("\nrunning url extractor agent")
            url_extraction_result = await Runner.run(url_extractor_agent, f"email_content: {"\n\n".join(all_content)}")
            print(url_extraction_result.final_output)


            print("\nrunning browser agent")
            final_answer = await Runner.run(browser_agent, f"user_query: {user_input}\nemail_search_result: {"\n\n".join(url_extraction_result.final_output.urls)}")
            print(final_answer)

asyncio.run(main())