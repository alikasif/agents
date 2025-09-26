from langchain_community.retrievers import ArxivRetriever
import time
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.tools import tool
from agents import function_tool

import logging

logging.basicConfig(level=logging.INFO) # Set the root logger level to INFO


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


@function_tool
def arxiv_search(args: str):
    """
    This tool searches the arxiv for the query that is being passed.
    This tool can be used for gathering the research done on the passed query

    Args:
        args: A single search query to execute

        
    Returns:
        a complete combined context 
    """

    logging.info(f"\n\n-- running arxiv_search for  {args}")
    
    retriever = ArxivRetriever(load_max_docs=2, get_full_documents=True,)
    docs = retriever.invoke(args)
    
    context = ""
    for doc in docs:
        #logging.info(f"\n {doc.page_content}")
        context+=doc.page_content
    
    return context


@tool
def think_tool(reflection: str) -> str:
    """Tool for strategic reflection on research progress and decision-making.

    Use this tool after each search to analyze results and plan next steps systematically.
    This creates a deliberate pause in the research workflow for quality decision-making.

    When to use:
    - After receiving search results: What key information did I find?
    - Before deciding next steps: Do I have enough to answer comprehensively?
    - When assessing research gaps: What specific information am I still missing?
    - Before concluding research: Can I provide a complete answer now?

    Reflection should address:
    1. Analysis of current findings - What concrete information have I gathered?
    2. Gap assessment - What crucial information is still missing?
    3. Quality evaluation - Do I have sufficient evidence/examples for a good answer?
    4. Strategic decision - Should I continue searching or provide my answer?

    Args:
        reflection: Your detailed reflection on research progress, findings, gaps, and next steps

    Returns:
        Confirmation that reflection was recorded for decision-making
    """
    return f"Reflection recorded: {reflection}"
