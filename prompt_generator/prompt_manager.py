from prompt_generator_agent import generate_prompt
from prompt_judging_agent import judge_prompts
from dotenv import load_dotenv
import asyncio


def generate_and_judge_prompts():
    """
    This function generates a prompt using the user's input and then judges the generated prompt.
    
    Args:
        None
        
    Returns:
        The final evaluation result of the judged prompt.
        
    Notes:
        This function uses asynchronous programming to run the prompt generation and judging tasks concurrently.
    """
    load_dotenv(override=True)

    # Ask for user input
    user_task = input("Enter your task description: ")

    gpt_result = asyncio.run(generate_prompt(user_task))
    # ...existing code...

    judge_result = asyncio.run(judge_prompts(user_task, gpt_result))
    print("\n--- Final Evaluation ---\n", judge_result)


if __name__ == "__main__":
    generate_and_judge_prompts()

