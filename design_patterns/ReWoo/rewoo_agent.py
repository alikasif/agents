
from langchain_anthropic import ChatAnthropic
import os
from dotenv import load_dotenv
import re
from prompt import planning_prompt,solve_prompt
from langchain_core.messages import HumanMessage
from googlesearch import search
import time
from typing import List
from typing_extensions import TypedDict
import pprint

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
        
        #print(f"\n\nthought response content :: {response["steps"]}\n\n")
        #self.messages.append(AIMessage(content= response))
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
        time.sleep(1)

        response = search(query, num_results=20, advanced=True)
        context = ""
        for result in response:
            context += result.description
        return context

    def _perform_action(self, tool, tool_input):
        print(f"\n\n tool: {tool} tool_input: {tool_input}")
        result=""
        if tool == "Google":
            result = self._google_search(tool_input)
        elif tool == "LLM":
            result = self.llm.invoke(tool_input).content
        else:
            raise ValueError

        return result


    def _execute(self, state: ReWOO):
        
        pattern = r"#(\w+)\s*=\s*(\w+)\[(.*)\]"
        step_results_dict = {}
        i=0
        
        for plan_step in state["steps"]:
            
            step = plan_step["step"]
            print(f"\nstep: {step}\n")
            matches = re.match(pattern, step)
            task_id, tool, tool_input = matches.groups()

            # replace place holders from previous steps result            
            for step_id, step_result in step_results_dict.items():      
                tool_input = tool_input.replace(step_id, step_result)
            
            result = self._perform_action(tool, tool_input)       
            step_results_dict["#"+task_id] = result
            i+=1

        return step_results_dict


    def _solve(self, state: ReWOO, step_results: dict):
        plan = ""
        pattern = r"#(\w+)\s*=\s*(\w+)\[(.*)\]"
        plan_steps = state["steps"]
        for plan_step in plan_steps:
            
            step = plan_step["step"]
            matches = re.match(pattern, step)
            task_id, tool, tool_input = matches.groups()
            result = step_results[task_id]

            print(f"plan_step: {plan_step}\n result: {result}\n\n")
            


        # for _plan, step_name, tool, tool_input in state["steps"]:
        #     _results = (state["results"] or {}) if "results" in state else {}
        #     for k, v in _results.items():
        #         tool_input = tool_input.replace(k, v)
        #         step_name = step_name.replace(k, v)
        #     plan += f"Plan: {_plan}\n{step_name} = {tool}[{tool_input}]"
        # prompt = solve_prompt.format(plan=plan, task=state["task"])
        # result = self.llm.invoke(prompt)
        # return {"result": result.content}



    def run(self, user_input):
        i =0
        next_prompt = user_input
        response=""
        rewoo = ReWOO()
        rewoo["task"] = user_input
        while i < 1:
            response = self._plan(rewoo)
            
            #print(f"\n\nPlan: {pprint.pprint(response)}")
            step_results = self._execute(response)
            #print(f"\n\n StepResults: {pprint.pprint(step_results)}\n\n")

            #self._solve(response, step_results)

            #response = self._parse_result_for_actions(response)
            #print(f"\n\nthought:: {response}")
            # action, action_input = self._parse_result_for_actions(result=response)
            # if action:
            #     print(f"\n\naction = {action} action_input = {action_input}")
            #     next_prompt = self._perform_action(action=action, action_input=action_input)
            #     #print(f"\n\nnext prompt {next_prompt}")
            # else:
            #     print(f"*** NO ACTION FOUND!!")
            i+=1
        return response


if __name__ == '__main__':

    load_dotenv(override=True)
    user_input = input("Enter your research query: ")
    agent = ReWooAgent(planning_prompt)
    response = agent.run(user_input=user_input)
    #print(f"\n\n final response: \n\n {response}")

