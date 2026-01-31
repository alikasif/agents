import sys
from agent import CommandLineAgent
from tools import execute_bash_command
from dotenv import load_dotenv
import os

load_dotenv()

def main():
    agent = CommandLineAgent(model_prefix="GEMINI")
    print("Command Line Agent Initialized. Type 'exit' to quit.")

    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                break

            print("Generating command and executing...")
            result = agent.generate_command(user_input)
            print(f"Agent Output:\n{result}")

            # Optional: Feedback loop can remain, but execution is now handled by the agent.
            feedback = input("\nFeedback (optional): ")
            if feedback:
                # For learning, we might need to parse the result to extract the command
                # But for now, just logging standard info
                agent.learn(user_input, "See Agent Output", feedback)
                print("Feedback recorded.")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
