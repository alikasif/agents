
from langchain_anthropic import ChatAnthropic
import os
from dotenv import load_dotenv
import re
from prompt import planning_prompt,solve_prompt
from langchain_core.messages import HumanMessage
import time
from typing import List
from typing_extensions import TypedDict
from langchain_community.utilities import GoogleSerperAPIWrapper


class PlanStep(TypedDict):
    plan: str
    step: str

class ReWOO(TypedDict):
    task: str
    steps: List[PlanStep]    
    finalResult: str

class StepResult(TypedDict):
    stepId: str
    result: str


class ReWooAgent:

    def __init__(self, system_prompt):
        self.messages = []
        
        # self.system_prompt = system_prompt
        # self.messages.append(SystemMessage(content= self.system_prompt))
        
        self.messages.append(HumanMessage(content= system_prompt))
        self.llm = ChatAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"), 
                                 model=os.getenv("ANTHROPIC_MODEL"),)
        
        self.planner = self.llm.with_structured_output(ReWOO)
        
        self.regex_pattern = r"Plan:\s*(.+)\s*(#E\d+)\s*=\s*(\w+)\s*\[([^\]]+)\]"
        #self.action_re = re.compile('^Action: (\w+): (.*)$')
        self.available_actions= {"google_search": self._google_search}
    

    def _plan(self, state: ReWOO):
        task = state["task"]

        self.messages.append(HumanMessage(content= task))

        response = self.planner.invoke(self.messages)
        
        return response
    

    # Definition of the tool 
    def _google_search(self, query:str) -> str:
        """
        This tool searches the internet for the query that is being passed.
        This tool can be used for gathering the latest information about the topic.
        This tool uses Google's Search, and returns the context based on the top results obtained.

        Args:
            query: prompt from the agent
        Returns:
            context(str): a complete combined context 
        """
        time.sleep(3)

        search = GoogleSerperAPIWrapper()
        results = search.run(query)
        return results
    
    def _llm_call(self, tool_input, plan):
        messages = [
            (
                "system",
                f"You are a helpful assistant. You must precisely answer based on the question: {plan}. Do not include any extra information.",
            ),
            ("human", tool_input),
        ]
        result = self.llm.invoke(messages).content
        #print(f"\n\nllm result: {result}")
        return result


    def _perform_action(self, tool, tool_input, plan):
        #print(f"\n\n tool: {tool} \ntool_input: {tool_input}")
        result=""
        if tool == "Google":
            return self._google_search(tool_input)
        elif tool == "LLM":
            return self._llm_call(tool_input, plan)
        else:
            raise ValueError

        return result


    def _execute(self, state: ReWOO):
        
        pattern = r"#(\w+)\s*=\s*(\w+)\[(.*)\]"
        step_results_dict = {}
        i=0
        
        for plan_step in state["steps"]:
            
            step = plan_step["step"]
            _plan = plan_step["plan"]
            #print(f"\nstep: {step}\n")
            matches = re.match(pattern, step)
            task_id, tool, tool_input = matches.groups()

            # replace place holders from previous steps result            
            for step_id, step_result in step_results_dict.items():   
                tool_input = tool_input.replace(step_id, step_result)
            
            result = self._perform_action(tool, tool_input, _plan)
            step_results_dict["#"+task_id] = result
            i+=1

        return step_results_dict


    def _solve(self, state: ReWOO, step_results: dict):
        
        pattern = r"#(\w+)\s*=\s*(\w+)\[(.*)\]"
        plan_steps = state["steps"]
        
        full_plan = ""
        for plan_step in plan_steps:
            
            step = plan_step["step"]
            _plan = plan_step["plan"]
            matches = re.match(pattern, step)
            task_id, _, _ = matches.groups()
            result = step_results["#"+task_id]
            full_plan += f"Plan: {_plan}\nResult: {result}\n"

        #pprint.pprint(full_plan)
        prompt = solve_prompt.format(plan=full_plan, task=state["task"])
        result = self.llm.invoke(prompt)
        return {"result": result.content}


    def run(self, user_input):
        i =0
        next_prompt = user_input
        response=""
        rewoo = ReWOO()
        rewoo["task"] = user_input
        response = self._plan(rewoo)
        
        #print(f"\n\nPlan: {pprint.pprint(response)}")
        step_results_dict = self._execute(response)
        #print(f"\n\n StepResults: {pprint.pprint(step_results_dict)}\n\n")

        solve_response = self._solve(response, step_results_dict)
        #print(f"Final response: {solve_response}")

        return solve_response


if __name__ == '__main__':

    load_dotenv(override=True)
    user_input = input("Enter your research query: ")
    agent = ReWooAgent(planning_prompt)
    response = agent.run(user_input=user_input)
    print(f"\n\n final response: \n\n {response}")

