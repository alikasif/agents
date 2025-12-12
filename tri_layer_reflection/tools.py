from typing import Annotated
from langchain_community.utilities import GoogleSerperAPIWrapper
from dotenv import load_dotenv
import os
from langchain.tools import tool

load_dotenv(override=True)
search = GoogleSerperAPIWrapper()

@tool
def google_search(
    query: Annotated[str, "The query to search for."],
) -> str:
    """Get the weather for a given location."""
    
    # Perform the search
    print(f"\n\nPerforming search for: {query}\n\n")
    results = search.run(query)
    return results

