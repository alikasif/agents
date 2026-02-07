
from agent import BrowserAgent
from utils import current_date_str


def browser(goal, user_input: list[str], file_name: str):
    
    agent = BrowserAgent(model_prefix="GEMINI")
    response = agent.run(
            topic=goal, content=user_input, current_date=current_date_str(), file_name=file_name
            )
    
    return response


if __name__ == "__main__":

    urls = [
        "https://github.com/sihyeong/Awesome-LLM-Inference-Engine",
        "https://multimodalai.substack.com/p/the-ai-engineers-guide-to-inference"        
    ]
    
    response = browser("Inference engine working", 
            urls, 
            "ai_blogger/agentic/blogs/inference_engine_working.md"
        )
    
    print("="*50)
    print(response.final_output)
