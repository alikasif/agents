import os
import json
from litellm import completion
from prompts import COMMAND_GENERATION_SYSTEM_PROMPT
from tools import execute_bash_command, run_powershell
from agents import Agent, Runner, OpenAIChatCompletionsModel
from agents.extensions.models.litellm_model import LitellmModel
import logging
import platform
from hooks import CustomHooks

logging.basicConfig(level=logging.INFO) # Set the root logger level to INFO
MAX_TURNS = 2


class CommandLineAgent:

    def __init__(self, model_prefix="GEMINI", history_file="history.json"):
        self.model_prefix = model_prefix
        self.history_file = history_file
        
        print(f"Using model: {self.model_prefix}")
        print(f"Using key {os.getenv('GEMINI_API_KEY')}")


    def get_model(self, prefix= None):        

        model = os.getenv(prefix+"_MODEL")
        api_key = os.getenv(prefix+"_API_KEY")
        base_url = os.getenv(prefix+"_BASE_URL")

        return LitellmModel(model=model, api_key=api_key)


    def get_agent(self):
        return Agent(
            name="Command Line Agent",
            model=self.get_model(self.model_prefix),
            instructions=COMMAND_GENERATION_SYSTEM_PROMPT,
            tools=[execute_bash_command, run_powershell],            
        )


    def generate_command(self, user_input: str) -> str:
        """
        Generates a bash command from user input using LiteLLM.
        """
        current_os = platform.system()
        my_hooks = CustomHooks()

        try:
            result = Runner.run_sync(self.get_agent(), 
            f"User: {user_input}\nOperating System: {current_os}\n", max_turns=MAX_TURNS, hooks=my_hooks
            )
            return result.final_output
        except Exception as e:
            print(f"Error generating command: {e}")
            return "Error generating command"


    def learn(self, user_input: str, generated_command: str, feedback: str):
        """
        Records the interaction and feedback to a history file.
        """
        interaction = {
            "input": user_input,
            "command": generated_command,
            "feedback": feedback
        }

        # Load existing history
        history = []
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r") as f:
                    history = json.load(f)
            except json.JSONDecodeError:
                pass # Start fresh if file is corrupt

        history.append(interaction)

        # Save updated history
        with open(self.history_file, "w") as f:
            json.dump(history, f, indent=4)
