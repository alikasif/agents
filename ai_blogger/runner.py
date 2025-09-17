from dotenv import load_dotenv
from analyst_agent import AnalystAgent
from researcher_agent import ResearcherAgent
from blog_writer_agent import BloggerAgent
from editor_agent import EditorAgent
from data_classes import TopicResearch
from prompt import analyst_prompt, researcher_prompt, blog_writer_prompt, editor_pompt, deep_research_prompt
import logging
import time
from utils import current_date_str

logging.basicConfig(level=logging.INFO) # Set the root logger level to INFO


def analysis(user_input: str):
    
    agent = AnalystAgent(analyst_prompt)
    response = agent.run(user_input=user_input, date_str=current_date_str())
    print(f"\n\n final response: \n\n {response}")
    return response.topics_to_research


def editor(topics_to_research):

    topics=[]
    i=1
    for topic in topics_to_research:
        topic = f"{i}. {topic}"
        topics.append(topic)
    all_topics = "\n".join(topics)

    prompt = editor_pompt.format(list_of_topics=all_topics)
    agent = EditorAgent(prompt)
    response = agent.run(user_input=all_topics)
    return response.ordered_topics


def research(topic_to_research):
   
    agent = ResearcherAgent(deep_research_prompt)
    time.sleep(10)
    response = agent.run(user_input=topic_to_research, date_str=current_date_str())
    print(f"\n\n\ntopic: {topic_to_research} \n\n final response: \n\n {response}")
    # detailed_researches.append(response.detailed_research)
    
    # pretty_printed_list = [item.model_dump() for item in detailed_researches]

    # pprint(pretty_printed_list)

    return response.detailed_research

def blog(user_input, detailed_research = TopicResearch):

    blog_writer_prompt_formatted = blog_writer_prompt.format(content=detailed_research.detailed_researched_content)
    blogger = BloggerAgent(blog_writer_prompt_formatted, user_input)
    
    blogger.write_blog()

load_dotenv(override=True)
#research("LLM Context Engineering")
user_input = input("Enter your research query: ")
topics_to_research = analysis(user_input)
topics_to_research = editor(topics_to_research) 
for topic in topics_to_research:
    detailed_research = research(topic)
    blog(user_input, detailed_research)


