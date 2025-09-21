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


def analysis(goal, user_input: str):
    
    agent = AnalystAgent(analyst_prompt)
    response = agent.run(goal=goal, user_input=user_input, date_str=current_date_str())
    print(f"\n\n final response: \n\n {response}")
    return response.topics_to_research


def editor(research_goal, topics_to_research):

    topics=[]
    i=1
    for topic in topics_to_research:
        topic = f"{i}. {topic}"
        topics.append(topic)
    all_topics = "\n".join(topics)

    prompt = editor_pompt.format(research_goal=research_goal, list_of_topics_to_read_about=all_topics)
    agent = EditorAgent(prompt)
    response = agent.run(user_input=all_topics)

    print(f"\n\n Editor Output: \n\n {response}")

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

def read_topic():
    """Read the topic.txt file and return its content as a string."""
    with open("./ai_blogger/topic.txt", "r", encoding="utf-8") as f:
        return f.read()
    
load_dotenv(override=True)
goal= "Evaluation of LLM Models & Applications. Approaches, Implementations and Frameworks"
research("1. Evaluation Metrics: What Needs to Be Measured   \
	        1.1. Generic Metrics: Accuracy, Recall, F1, Coherence, Perplexity, Latency   \
	        1.2. LLM-Specific Metrics: Hallucination, Faithfulness, Relevancy, Task Completion, Contextual Precision, Tool Correctness, Bias, Toxicity, Summarization, Prompt Alignment, Custom Metrics   \
	        1.3. Characteristics of Good Metrics (Quantitative, Reliable, Accurate, Human-Correlated)"
         )
# user_input = read_topic()
# topics_to_research = analysis(goal, user_input)
# topics_to_research = editor(goal, topics_to_research) 
# for topic in topics_to_research[:3]:
#     detailed_research = research(topic)
#     blog(goal, detailed_research)


