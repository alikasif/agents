from langchain_community.retrievers import ArxivRetriever
import time
import asyncio
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.tools import tool
from agents import function_tool
from langchain_tavily import TavilySearch
from dotenv import load_dotenv
import logging
import os

logging.basicConfig(level=logging.INFO)


async def _extract_page_content_async(url: str, wait_seconds: int = 2) -> dict:
    """
    Internal async function to fetch a web page using Playwright.
    Handles both static and dynamic (JavaScript-rendered) content.
    """
    from playwright.async_api import async_playwright
    
    logging.info(f"\n\n-- browsing {url}")
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            
            await page.goto(url, timeout=30000, wait_until="domcontentloaded")
            await page.wait_for_timeout(wait_seconds * 1000)
            
            title = await page.title() or "No title"
            
            content = await page.evaluate("""() => {
                const selectors = ['script', 'style', 'nav', 'footer', 'header', 'aside', 'noscript', 'iframe'];
                selectors.forEach(sel => {
                    document.querySelectorAll(sel).forEach(el => el.remove());
                });
                const main = document.querySelector('article') || 
                             document.querySelector('main') || 
                             document.querySelector('[role="main"]') ||
                             document.querySelector('.content') ||
                             document.querySelector('body');
                return main ? main.innerText : '';
            }""")
            
            key_points = await page.evaluate("""() => {
                const headings = document.querySelectorAll('h1, h2, h3');
                return Array.from(headings)
                    .map(h => h.innerText.trim())
                    .filter(text => text.length > 3)
                    .slice(0, 20);
            }""")
            
            await browser.close()
            
            lines = [line.strip() for line in content.split("\n") if line.strip()]
            content = "\n".join(lines)
            
            max_length = 15000
            if len(content) > max_length:
                content = content[:max_length] + "\n\n[Content truncated...]"
            
            return {
                "url": url,
                "title": title,
                "content": content,
                "key_points": key_points,
                "error": None
            }
            
    except Exception as e:
        logging.error(f"Failed to browse {url}: {str(e)}")
        return {
            "url": url,
            "title": None,
            "content": None,
            "key_points": [],
            "error": str(e)
        }


def _extract_page_content(url: str, wait_seconds: int = 2) -> dict:
    """Wrapper to run async function from sync context within existing event loop."""
    try:
        loop = asyncio.get_running_loop()
        import nest_asyncio
        nest_asyncio.apply()
        return loop.run_until_complete(_extract_page_content_async(url, wait_seconds))
    except RuntimeError:
        return asyncio.run(_extract_page_content_async(url, wait_seconds))


@function_tool
def browse_url(url: str) -> dict:
    """
    Browses a web page and extracts its content, title, and key points.
    Works with both static HTML pages and dynamic JavaScript-rendered pages.
    
    Args:
        url: The URL to browse and extract content from
    
    Returns:
        A dictionary containing:
        - url: The source URL
        - title: Page title
        - content: Full text content of the page
        - key_points: List of headings/key sections found
        - error: Error message if fetch failed (None otherwise)
    """
    return _extract_page_content(url)


@function_tool
def browse_urls(urls: list[str]) -> list[dict]:
    """
    Browses multiple web pages and extracts their content.
    Works with both static HTML pages and dynamic JavaScript-rendered pages.
    
    Args:
        urls: List of URLs to browse and extract content from
    
    Returns:
        List of dictionaries, each containing url, title, content, key_points, and error
    """
    logging.info(f"\n\n-- browsing {len(urls)} URLs")
    
    results = []
    for url in urls:
        result = _extract_page_content(url)
        results.append(result)
        time.sleep(1)
    
    return results


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


# @function_tool
# def browse_urls(urls: list[str]) -> str:
#     """
#     This tool navigates to web page and extracts their content using a headless browser.
#     It uses Playwright to automate browser interactions and retrieve page elements.
    
#     Args:
#         url: URLs to browse and extract content from        
    
#     Returns:
#         Combined text content from the page, joined by newlines
#     """

#     logging.info(f"\n\n-- running browse_urls for  {urls}")

#     sync_browser = create_sync_playwright_browser()
#     toolkit = PlayWrightBrowserToolkit.from_browser(sync_browser=sync_browser)
#     tools = toolkit.get_tools()

#     tools_by_name = {tool.name: tool for tool in tools}
#     navigate_tool = tools_by_name["navigate_browser"]
#     get_elements_tool = tools_by_name["get_elements"]
    
#     logging.info(f"\n\n-- browsing each url using tools")

#     responses =[]
#     for url in urls:
#         logging.info(f"\n\n-- running browse for {url}")
#         navigate_tool.run(url)
#         response = get_elements_tool.run("body")
#         responses.append(response)
    
#     return "\n".join(responses)


# @function_tool
# def browse(url: str) -> str:
#     """
#     This tool navigates to web page and extracts their content using a headless browser.
#     It uses Playwright to automate browser interactions and retrieve page elements.
    
#     Args:
#         url: A URL to browse and extract content from        
    
#     Returns:
#         Combined text content from the page, joined by newlines
#     """
#     sync_browser = create_sync_playwright_browser()
#     toolkit = PlayWrightBrowserToolkit.from_browser(sync_browser=sync_browser)
#     tools = toolkit.get_tools()

#     tools_by_name = {tool.name: tool for tool in tools}
#     navigate_tool = tools_by_name["navigate_browser"]
#     get_elements_tool = tools_by_name["get_elements"]
    
#     responses =[]
#     logging.info(f"\n\n-- running browse for  {url}")
#     navigate_tool.run(url)
#     response = get_elements_tool.run("body")
#     responses.append(response)
    
#     return "\n".join(responses)
