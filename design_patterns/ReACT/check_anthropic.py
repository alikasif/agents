from langchain_anthropic import ChatAnthropic
import os
from dotenv import load_dotenv


load_dotenv(override=True)
print(os.getenv("ANTHROPIC_API_KEY"))
print(os.getenv("ANTHROPIC_MODEL"))
print(os.getenv("ANTHROPIC_BASE_URL"))

llm = ChatAnthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY"), 
    model=os.getenv("ANTHROPIC_MODEL"),
    #base_url=os.getenv("ANTHROPIC_BASE_URL")
    )

print(llm.invoke("what is wikipedia?"))
