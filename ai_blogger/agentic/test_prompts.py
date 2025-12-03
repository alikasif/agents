
import asyncio
import os
from dotenv import load_dotenv
from blog_writer_agent import AnalystAgent, ResearchAgent, BloggerAgent, EditorAgent
from utils import current_date_str

# Load environment variables
load_dotenv(override=True)

# Mock data
goal = "LLM Context Compaction"
content = """
Context compaction is a technique used to reduce the size of the context window in Large Language Models (LLMs) without significantly losing information. 
This is crucial for handling long documents or conversation histories within the token limits of models. 
Techniques include summarization, selective token dropping, and vector embedding compression.
"""

async def test_flow():
    print("--- Testing Analyst Agent ---")
    analyst = AnalystAgent()
    try:
        analysis_result = await analyst.run(current_date=current_date_str(), topic=goal, content=content)
        print(f"Analyst Output Topics: {len(analysis_result.topics)}")
        if not analysis_result.topics:
            print("No topics found!")
            return
    except Exception as e:
        print(f"Analyst Agent Failed: {e}")
        return

    first_topic = analysis_result.topics[0]
    print(f"Testing with First Topic: {first_topic.topic}")
    print(f"Subtopics: {first_topic.sub_topics}")

    print("\n--- Testing Research Agent ---")
    researcher = ResearchAgent()
    try:
        research_result = await researcher.run(topic=first_topic)
        print("Research Output Length:", len(research_result.research))
        print("Research Output Preview:", research_result.research[:200])
    except Exception as e:
        print(f"Research Agent Failed: {e}")
        return

    print("\n--- Testing Blogger Agent ---")
    blogger = BloggerAgent()
    try:
        blog_post = await blogger.run(research=research_result.research)
        # BloggerAgent returns a string (result.final_output)
        print("Blog Post Length:", len(str(blog_post)))
        print("Blog Post Preview:", str(blog_post)[:200])
    except Exception as e:
        print(f"Blogger Agent Failed: {e}")
        return

    print("\n--- Testing Editor Agent ---")
    editor = EditorAgent()
    try:
        edited_blog = await editor.run(research=str(blog_post))
        # EditorAgent returns a string
        print("Edited Blog Length:", len(str(edited_blog)))
    except Exception as e:
        print(f"Editor Agent Failed: {e}")
        return
    
    # Save to file for inspection
    os.makedirs("test_output", exist_ok=True)
    with open("test_output/final_blog.md", "w", encoding="utf-8") as f:
        f.write(str(edited_blog))
    print("Saved final blog to test_output/final_blog.md")

if __name__ == "__main__":
    asyncio.run(test_flow())
