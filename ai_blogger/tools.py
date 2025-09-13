from langchain_community.retrievers import ArxivRetriever
import time
from googlesearch import search
from langchain_community.utilities import GoogleSerperAPIWrapper
import logging
from dotenv import load_dotenv
import os
import requests

logging.basicConfig(level=logging.INFO) # Set the root logger level to INFO

def google_search2(query: str):
    load_dotenv(override=True)
    
    API_KEY = os.getenv("GOOGLE_API_KEY")
    CX_ID = os.getenv("GOOGLE_CUSTOM_SEARCH_ENGINE_ID")

    url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={CX_ID}&q={query}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        search_results = response.json()

        for item in search_results.get("items", []):
            print(f"Title: {item.get('title')}")
            print(f"Link: {item.get('link')}")
            print(f"Snippet: {item.get('snippet')}\n\n")

    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")

def google_search(query:str) -> str:
        """
        This tool searches the internet for the query that is being passed.
        This tool can be used for gathering the latest information about the topic.
        This tool uses Google's Search, and returns the context based on the top results obtained.

        Args:
            query: prompt from the agent
        Returns:
            context(str): a complete combined context 
        """
        time.sleep(5)
        logging.info(f"\n\n-- running google_serch for  {query}")

        # response = search(query, num_results=20, advanced=True)
        # context = ""
        # for result in response:
        #     context += result.description
        # return context

        search = GoogleSerperAPIWrapper()
        results = search.run(query)
        return results


def arxiv_search(args: str):
    logging.info(f"\n\n-- running arxiv_search for  {args}")
    
    retriever = ArxivRetriever(load_max_docs=2, get_full_documents=True,)
    docs = retriever.invoke(args)
    
    context = ""
    for doc in docs:
        #logging.info(f"\n {doc.page_content}")
        context+=doc.page_content
    
    return context


#google_search2("context engineering LLM")