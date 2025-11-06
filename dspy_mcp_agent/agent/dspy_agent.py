from dotenv import load_dotenv
import dspy
import instructor
from typing import List, Any, Callable, Optional
from pydantic import BaseModel

load_dotenv()
dspy.configure(lm=dspy.LM("openai/gpt-4o-mini"))

class Plan(dspy.Signature):
    """Produce a step by step plan to perform the task.
    The plan needs to be in markdown format and should be broken down into big steps (with ## headings) and sub-steps beneath those.
    When thinking about your plan, be sure to think about the tools at your disposal and include them in your plan.
    """
    task = dspy.InputField(prefix="Task", desc="The task")
    context = dspy.InputField(format=str, desc="The context around the plan")
    proposed_plan = dspy.OutputField(desc="The proposed, step by step execution plan.")
    

class Worker(dspy.Module):
    """An agent that can plan and use tools to accomplish a task."""
    def __init__(self, role:str, tools:List):
        self.role = role
        self.tools = tools
        self.tool_descriptions = "\n".join([f"- {t.name}: {t.description}. To use this tool please provide: `{t.requires}`" for t in tools])
        self.plan = dspy.ChainOfThought(Plan)

    def forward(self, task:str):
        context = f"{self.role}\n{self.tool_descriptions}"
        input_args = dict(
            context = context,
            task = task
        ) # just did args for printing for debugging
        result = self.plan(**input_args)
        print(result.proposed_plan)


class Worker2(dspy.Module):

    def __init__(self, role:str, tools:List):
        self.role = role
        self.tools = dict([(t.name, t) for t in tools])
        self.tool_descriptions = "\n".join([f"- {t.name}: {t.description}. To use this tool please provide: `{t.requires}`" for t in tools])
        self._plan = dspy.ChainOfThought(Plan)
        self._tool = dspy.ChainOfThought("task, context -> tool_name, tool_argument")

        print(self.tool_descriptions)


    def plan(self, task:str, feedback:Optional[str]=None):
        context = f"Your role:{self.role}\n Tools at your disposal:\n{self.tool_descriptions}"
        if feedback:
            context += f"\nPrevious feedback on your prior plan {feedback}"
        input_args = dict(
            task=task,
            context=context
        )
        result = self._plan(**input_args)
        return result.proposed_plan


    def execute(self, task:str, use_tool:bool):
        print(f"executing {task}")
        if not use_tool:
            return f"{task} completed successfully"

        res = self._tool(task=task, context=self.tool_descriptions)
        t = res.tool_name
        arg = res.tool_argument
        if t in self.tools:
            complete = self.tools[t].func(arg)
            return complete
        return "Not done"
    

class Tool(BaseModel):
    name: str
    description: str
    requires: str
    func: Callable

test_tools = [
    Tool(name="phone", description="a way of making phone calls", requires="phone_number", func=lambda x: "they've got time"),
    Tool(name="local business lookup", description="Look up businesses by category", requires="business category", func=lambda x: "Bills landscaping: 415-555-5555")
]

worker = Worker2("assistant", test_tools)
worker("Write a blog about LLM")
# you'll see output you might expect.