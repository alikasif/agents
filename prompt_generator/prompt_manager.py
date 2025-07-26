from prompt_generator_agent import generate_prompt
from prompt_judging_agent import judge_prompts
from dotenv import load_dotenv
import asyncio

def generate_and_judge_prompts():
    load_dotenv(override=True)

    # Ask for user input
    user_task = input("Enter your task description: ")

    gpt_result = asyncio.run(generate_prompt(user_task))
    #print("\n--- Judge Agent 1 (GPT) Evaluation ---\n", gpt_result)

    #judge_result = asyncio.run(run_judging_agent(user_task, gpt_result))
    #print("\n--- Judge Agent 1 (GPT) Evaluation ---\n", judge_result)

    judge_result = asyncio.run(judge_prompts(user_task, gpt_result))
    print("\n--- Final Evaluation ---\n", judge_result)


if __name__ == "__main__":
    generate_and_judge_prompts()

