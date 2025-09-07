from langchain_community.retrievers import ArxivRetriever
import time
from googlesearch import search
from langchain_community.utilities import GoogleSerperAPIWrapper
import logging

logging.basicConfig(level=logging.INFO) # Set the root logger level to INFO


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
        time.sleep(3)
        logging.info(f"\n\n-- running google_serch for  {query}")

        # response = search(query, num_results=20, advanced=True)
        # context = ""
        # for result in response:
        #     context += result.description
        # return context

        search = GoogleSerperAPIWrapper()
        results = search.run("latest news on AI")
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


#arxiv_search("chain of agents llm")