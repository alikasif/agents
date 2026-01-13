from langchain_community.retrievers import ArxivRetriever
import time
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.tools import tool
from agents import function_tool
from langchain_tavily import TavilySearch
from dotenv import load_dotenv
from structured_output import *
import logging
import os
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain_community.tools.playwright.utils import (
    create_sync_playwright_browser,
)


logging.basicConfig(level=logging.INFO) # Set the root logger level to INFO


@function_tool
def blog_writer(blog_name: str, content: str) -> str:
    """
    This tool writes the content to the file
    Args:
        blog_name: name of the blog
        content: content to write to the file
    Returns:
        confirmation that content was written to the file
    """
    print(f"\n\nWriting blog {blog_name} to {content}\n\n")
    
    directory_path = f".\\ai_blogger\\agentic\\blogs\\{blog_name}"
    os.makedirs(directory_path, exist_ok=True)
    
    with open(f"{directory_path}\\{blog_name}.md", "a") as file_object:
        # Write the new content to the file
        try:
            file_object.write(content)
        except:
            print(f"failed while writing {content}\n\n")
        
        file_object.write("\n\n")
    
    print(f"\n\nWritten Blog {blog_name} \n\n")


@function_tool
def file_writer(file_path: str, content: Outline) -> str:
    """
    This tool writes the content to the file
    Args:
        file_path: path to the file
        content: content to write to the file
    Returns:
        confirmation that content was written to the file
    """
    print(f"\n\nWriting content {content} to {file_path}\n\n")

    with open(file_path, "a", encoding="utf-8") as f:
        print(f"opening file {file_path} to write {str(content)}")

        for topic in content.topics:
            f.write(str(topic))
            f.write("\n\n")

    return f"Content written to {file_path}"


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


@function_tool
def browse(url: str) -> str:
    """
    This tool navigates to web page and extracts their content using a headless browser.
    It uses Playwright to automate browser interactions and retrieve page elements.
    
    Args:
        url: A URL to browse and extract content from        
    
    Returns:
        Combined text content from the page, joined by newlines
    """
    sync_browser = create_sync_playwright_browser()
    toolkit = PlayWrightBrowserToolkit.from_browser(sync_browser=sync_browser)
    tools = toolkit.get_tools()

    tools_by_name = {tool.name: tool for tool in tools}
    navigate_tool = tools_by_name["navigate_browser"]
    get_elements_tool = tools_by_name["get_elements"]
    
    responses =[]
    logging.info(f"\n\n-- running browse for  {url}")
    navigate_tool.run(url)
    response = get_elements_tool.run("body")
    responses.append(response)
    
    return "\n".join(responses)


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


# load_dotenv(override=True)
# tavily_google_search("what is US shutdown?")