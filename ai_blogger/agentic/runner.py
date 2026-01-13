from dotenv import load_dotenv
import logging
import time
import json
from utils import *
from blog_writer_agent import *
import asyncio


load_dotenv(override=True)

logging.basicConfig(level=logging.INFO) # Set the root logger level to INFO


def analysis(goal, user_input: str, file_name: str):
    
    agent = AnalystAgent(model_prefix="GEMINI")
    response = agent.run(
            topic=goal, content=user_input, current_date=current_date_str(), file_name=file_name
            )
    
    return response


def research(topic_to_research: Topic):
   
    agent = ResearchAgent(model_prefix="GEMINI")
    time.sleep(10)
    response = agent.run(topic=topic_to_research)
    return response


def blog(blog_name: str, detailed_research: str):

    response = BloggerAgent(model_prefix="GEMINI").run(blog_name, detailed_research)
    return response


def edit(blog_name: str, blog: str):
    editor_agent = EditorAgent(model_prefix="GEMINI")
    if not editor_agent:
        print("EditorAgent not initialized properly.")
        return
    
    edited_blog_name = f"{blog_name}_edited"
    response = editor_agent.run(edited_blog_name, blog)
    return response

def start():
    
    goal= "Reasoning Models. How they work?"
    blog_name = "reasoning_models_blog"

    topics_file_name=f".\\ai_blogger\\agentic\\inputs\\{blog_name}_topics.txt"
    analyst_file_name=f".\\ai_blogger\\agentic\\inputs\\{blog_name}_analyst_output.txt"
    progress_file_name=f".\\ai_blogger\\agentic\\inputs\\{blog_name}_progress.json"

    response = None

    if not os.path.exists(analyst_file_name):
        while True:
            user_input = read_topic(topics_file_name)
            response = analysis(goal, user_input, analyst_file_name)

            shall_continue = input("Do you want to continue with research and blog writing? (yes/no): ").strip().lower()
            
            if shall_continue not in ['yes', 'y']:
                print("\n\nre running the analysis...")
            else:
                break


    topics = []
    #add a logic to read the topics to research from the file and map it to Topic objects
    with open(analyst_file_name, "r", encoding="utf-8") as f:
        response = f.read()
        print(f"\n\n final response: \n\n {response}")
        for topic in response.splitlines():
            if topic:
                topics.append(Topic.from_string(topic))
        #topics = [Topic(topic=topic) for topic in response.splitlines()]

    print(topics)

    print(f"\n\n total topics: {len(topics)}")

    #Load completed topics to resume from where we left off
    completed_topics = load_completed_topics(progress_file_name)
    
    if completed_topics:
        print(f"\nResuming progress. Already completed {len(completed_topics)} topic(s):")
        for t in completed_topics:
            print(f"  - {t}")


    for topic in topics:

        #Skip topics that have already been completed
        if topic.topic in completed_topics:
            print(f"\nSkipping already completed topic: {topic.topic}")
            continue
        
        print(f"\ntopic: {topic.topic}")

        detailed_research = research(topic)
        print(f"\ndetailed research: {detailed_research}")

        blog_response = blog(blog_name, detailed_research.research)
        print(f"\nblog response: {blog_response}")
        
        #Mark topic as completed and save progress
        save_completed_topic(progress_file_name, topic.topic)

    print("\nAll topics processed successfully!")

    blog_file_path = f".\\ai_blogger\\agentic\\blogs\\{blog_name}\\{blog_name}.md"
        
    content = read_blog(blog_file_path)
    edit(blog_name, content)

if __name__ == "__main__":
    start()
