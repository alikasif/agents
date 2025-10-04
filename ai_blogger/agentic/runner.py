from dotenv import load_dotenv
import logging
import time
from utils import current_date_str
from blog_writer_agent import *
import asyncio

logging.basicConfig(level=logging.INFO) # Set the root logger level to INFO


def analysis(goal, user_input: str):
    
    agent = AnalystAgent()
    response = asyncio.run(agent.run(topic=goal, content=user_input, current_date=current_date_str()))
    #print(f"\n\n final response: \n\n {response}")

    for topic in response.topics:
        print(topic.topic)
        print("\n")
        print(topic.sub_topics)
        print("\n\n")
    return response


def research(topic_to_research: Topic):
   
    agent = ResearchAgent()
    time.sleep(10)
    response = asyncio.run(agent.run(topic=topic_to_research))
    return response


def blog(blog_name: str, detailed_research: str):

    response = asyncio.run(BloggerAgent().run(detailed_research))
    
    with open(f".\\ai_blogger\\agentic\\blogs\\{blog_name}.md", "a") as file_object:
        # Write the new content to the file
        file_object.write(str(response))
        file_object.write("\n\n")
    

def edit(blog_name: str, blog: str):
    editor_agent = EditorAgent()
    if not editor_agent:
        print("EditorAgent not initialized properly.")
        return
    
    response = asyncio.run(EditorAgent().run(blog))
    
    with open(f".\\ai_blogger\\agentic\\blogs\\{blog_name}_edited.md", "a") as file_object:
        # Write the new content to the file
        file_object.write(str(response))
        file_object.write("\n\n")


def read_topic():
    """Read the topic.txt file and return its content as a string."""
    with open("./ai_blogger/rag_topic.txt", "r", encoding="utf-8") as f:
        return f.read()

def read_blog(blog_name: str):
    """Read the specified blog markdown file and return its content as a string."""
    with open(f"./ai_blogger/agentic/blogs/{blog_name}.md", "r", encoding="utf-8") as f:
        return f.read()


load_dotenv(override=True)

# goal= "RAG and its different implementations and how it stands against long context models"
# user_input = read_topic()

# response = analysis(goal, user_input)

# shall_continue = input("Do you want to continue with research and blog writing? (yes/no): ").strip().lower()
# if shall_continue not in ['yes', 'y']:
#     print("Exiting the program.")
#     exit(0)

# for topic in response.topics:
#     print(f"\ntopic: {topic.topic}")

#     detailed_research = research(topic)

#     blog("rag", detailed_research.research)

content = read_blog("rag")
edit("rag", content)