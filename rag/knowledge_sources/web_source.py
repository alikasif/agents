from langchain_community.utilities import GoogleSerperAPIWrapper
import time
from rag.knowledge_sources.abstract_datasource import AbstractDataSource
import logging
from typing import List

logging.basicConfig(level=logging.INFO) # Set the root logger level to INFO

class WebSource(AbstractDataSource):

    def __init__(self):
        pass


    def search(self, query: str) -> List[str]:
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
        search = GoogleSerperAPIWrapper()
        
        for query in queries:

            time.sleep(5)
            logging.info(f"\n\n-- running google_search for  {query}")            
            result = search.run(query)
            results.append(result)

        return results

    def about(self) -> str:
        return "This is a Web source that uses Google Search for retrieving information."
    
    def short_name(self) -> str:
        return "web_search"
