from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.tools import Tool
from dotenv import load_dotenv

load_dotenv(override=True)
search = GoogleSerperAPIWrapper()

def get_google_search_tool():
    
    return Tool(
            name="Google_Search",
            func=search.run,
            description="useful for when you need to ask with search",
        )
    