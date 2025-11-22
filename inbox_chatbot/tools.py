import time
from agents import function_tool
from langchain_tavily import TavilySearch
from dotenv import load_dotenv
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.document_loaders import WebBaseLoader

import logging

logging.basicConfig(level=logging.INFO) # Set the root logger level to INFO


@function_tool
def web_fetch(url: str) -> str:
    """
    This tool fetches the content of a given URL.

    Args:
        url: The URL to fetch content from.

    Returns:
        The text content of the webpage.
    """
    logging.info(f"\n\n-- running web_fetch for ::  {url}")
    loader = WebBaseLoader(url)
    docs = loader.load()
    combined_text = "\n".join([doc.page_content for doc in docs])

    logging.info(f"\n\n-- fetched content: {(combined_text)} ")
    
    return combined_text
    

def tavily_google_search(query: str) -> str:
    """
    This tool searches the internet for the query that is being passed.
    This tool can be used for gathering the latest information about the topic.
    This tool uses Google's Search, and returns the context based on the top results obtained.

    Args:
        query: A single search query to execute


    Returns:
        a complete combined context 
    """
    tool = TavilySearch(
            max_results=5,
            topic="general",
            # include_answer=False,
            # include_raw_content=False,
            # include_images=False,
            # include_image_descriptions=False,
            # search_depth="basic",
            # time_range="day",
            # start_date=None,
            # end_date=None,
            # include_domains=None,
            # exclude_domains=None
        )
    results = tool.invoke({"query": query})
    print(results)

@function_tool
def google_search(query:str) -> str:
        """
        This tool searches the internet for the query that is being passed.
        This tool can be used for gathering the latest information about the topic.
        This tool uses Google's Search, and returns the context based on the top results obtained.

        Args:
            query: A single search query to execute


        Returns:
            a complete combined context 
        """

        results = []
        queries = query.split(",")
        for query in queries:
            time.sleep(5)
            logging.info(f"\n\n-- running google_search for  {query}")
            search = GoogleSerperAPIWrapper()
            result = search.run(query)
            results.append(result)
        return "\n".join(results)
