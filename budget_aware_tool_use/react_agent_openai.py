
import re
import json
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from budget_tracker import BudgetTracker
from dataclasses import dataclass
from dotenv import load_dotenv
from budget_tracker import BudgetTracker
from tools import execute_tool
from config import ModelConfig, BudgetConfig, DEFAULT_MODEL_CONFIG, DEFAULT_BUDGET_CONFIG
from prompts import get_react_budget_prompt
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import traceback

load_dotenv(override=True)


@dataclass
class ReActStep:
    """Represents a single reasoning step in the ReAct loop"""
    step_num: int
    thought: str
    action: Optional[Dict[str, Any]] = None
    observation: Optional[str] = None
    answer: Optional[str] = None


class OpenAIReActAgent:
    """
    ReAct agent powered by OpenAI with budget awareness.
    
    The agent follows the ReAct pattern:
    1. Thought: Reason about the current state and what to do next
    2. Action: Call a tool (search/browse) or provide final answer
    3. Observation: Observe the result of the action
    4. Repeat until answer is found or budget depleted
    """
    
    def __init__(
        self,
        model_config: Optional[ModelConfig] = None,
        budget_config: Optional[BudgetConfig] = None,
        model_name: str = os.getenv("GEMINI_MODEL", "gemini-3.0-flash"),
        max_iterations: int = 15,
        verbose: bool = True
    ):
        """
        Initialize the OpenAI ReAct agent.
        
        Args:
            model_config: Model configuration (temperature, etc.)
            budget_config: Budget limits and thresholds
            model_name: OpenAI model to use
            max_iterations: Maximum reasoning iterations
            verbose: Print step-by-step reasoning
        """
        self.model_config = model_config or DEFAULT_MODEL_CONFIG
        self.budget_config = budget_config or DEFAULT_BUDGET_CONFIG
        self.model_name = os.getenv("OPENAI_MODEL", model_name)
        self.max_iterations = max_iterations
        self.verbose = verbose
        
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL"))
        self.budget_tracker = BudgetTracker(self.budget_config)
        self.steps: List[ReActStep] = []
    
    
    def run(self, question: str) -> Dict[str, Any]:
        """
        Execute the ReAct loop to answer a question.
        
        Args:
            question: The question to answer
            
        Returns:
            Dictionary containing answer, steps, and budget usage
        """
        if self.verbose:
            print(f"\n{'='*80}")
            print(f"Question: {question}")
            print(f"{'='*80}\n")
        
        # Reset state
        self.budget_tracker.reset()
        self.steps = []
        
        # Initialize conversation with system prompt
        messages = []
        
        for iteration in range(1, self.max_iterations + 1):
            if self.verbose:
                print(f"\n--- Iteration {iteration} ---")
            
            # Get current budget guidance
            budget_guidance = self.budget_tracker.get_strategy_guidance()
            
            # Build system prompt with budget awareness
            if iteration == 1:
                system_prompt = get_react_budget_prompt(budget_guidance)
                messages.append({"role": "system", "content": system_prompt})
                user_message = f"Question: {question}\n\nBegin reasoning."
            else:
                user_message = "Continue reasoning based on the observation."
            
            # Add budget status to user message
            budget_status = self.budget_tracker.format_budget_message()
            user_message = f"{user_message}\n\n{budget_status}"
            
            messages.append({"role": "user", "content": user_message})
            
            # Get LLM response
            try:               
                
                response = self.client.invoke(messages)

                assistant_message = response.content[0]["text"]                        
                
                messages.append({"role": "assistant", "content": assistant_message})
                
                if self.verbose:
                    print(f"\nAgent Response:\n{assistant_message}\n")
                
                # Parse the response
                step = self._parse_response(assistant_message, iteration)
                self.steps.append(step)
                
                # Check if we have a final answer
                if step.answer:
                    if self.verbose:
                        print(f"\n{'='*80}")
                        print(f"Final Answer: {step.answer}")
                        print(f"{'='*80}\n")
                    
                    return {
                        "answer": step.answer,
                        "steps": self.steps,
                        "iterations": iteration,
                        "budget_used": {
                            "queries": self.budget_tracker.query_used,
                            "urls": self.budget_tracker.url_used
                        }
                    }
                
                # Execute tool if action is present
                if step.action:
                    observation = self._execute_action(step.action)
                    step.observation = observation
                    
                    # Add observation as user message
                    messages.append({
                        "role": "user",
                        "content": f"Tool Response:\n{observation}"
                    })
                    
                    if self.verbose:
                        print(f"Observation:\n{observation}\n")
                
            except Exception as e:
                if self.verbose:
                    print(f"Error in iteration {iteration}: {e}")
                    traceback.print_exc()
                
                return {
                    "answer": "Error during execution",
                    "error": str(e),
                    "steps": self.steps,
                    "iterations": iteration,
                    "budget_used": {
                        "queries": self.budget_tracker.query_used,
                        "urls": self.budget_tracker.url_used
                    }
                }
        
        # Max iterations reached
        if self.verbose:
            print(f"\nMax iterations ({self.max_iterations}) reached.")
        
        return {
            "answer": "None",
            "reason": "Maximum iterations reached",
            "steps": self.steps,
            "iterations": self.max_iterations,
            "budget_used": {
                "queries": self.budget_tracker.query_used,
                "urls": self.budget_tracker.url_used
            }
        }
    
    
    def _parse_response(self, response: str, step_num: int) -> ReActStep:
        """
        Parse the agent's response to extract thought, action, or answer.
        
        Args:
            response: Raw response from the LLM
            step_num: Current step number
            
        Returns:
            Parsed ReActStep
        """
        step = ReActStep(step_num=step_num, thought="")
        
        # Extract <think> block
        think_match = re.search(r'<think>(.*?)</think>', response, re.DOTALL | re.IGNORECASE)
        if think_match:
            step.thought = think_match.group(1).strip()
        
        # Extract <answer> block
        answer_match = re.search(r'<answer>(.*?)</answer>', response, re.DOTALL | re.IGNORECASE)
        if answer_match:
            step.answer = answer_match.group(1).strip()
            return step
        
        # Extract <tool_code> block
        tool_match = re.search(r'<tool_code>(.*?)</tool_code>', response, re.DOTALL | re.IGNORECASE)
        if tool_match:
            tool_json_str = tool_match.group(1).strip()
            
            # Handle markdown code blocks
            if "```" in tool_json_str:
                json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', tool_json_str, re.DOTALL)
                if json_match:
                    tool_json_str = json_match.group(1).strip()
            
            try:
                step.action = json.loads(tool_json_str)
            except json.JSONDecodeError as e:
                if self.verbose:
                    print(f"Warning: Failed to parse tool JSON: {e}")
                    print(f"Raw JSON: {tool_json_str}")
        
        return step
    
    
    def _execute_action(self, action: Dict[str, Any]) -> str:
        """
        Execute a tool action and track budget usage.
        
        Args:
            action: Dictionary with 'tool' and 'arguments' keys
            
        Returns:
            String observation from the tool execution
        """
        tool_name = action.get("tool")
        tool_args = action.get("arguments", {})
        
        if not tool_name:
            return json.dumps({"error": "No tool specified in action"})
        
        # Check budget before execution
        if tool_name == "search":
            queries = tool_args.get("queries", [])
            query_count = len(queries)
            
            if not self.budget_tracker.can_use_tool("search", query_count):
                return json.dumps({
                    "error": f"Insufficient query budget. Requested: {query_count}, Remaining: {self.budget_tracker.get_remaining('search')}"
                })
            
            self.budget_tracker.track_tool_usage("search", query_count)
        
        elif tool_name == "browse":
            urls = tool_args.get("urls", [])
            url_count = len(urls)
            
            if not self.budget_tracker.can_use_tool("browse", url_count):
                return json.dumps({
                    "error": f"Insufficient URL budget. Requested: {url_count}, Remaining: {self.budget_tracker.get_remaining('browse')}"
                })
            
            self.budget_tracker.track_tool_usage("browse", url_count)
        
        # Execute the tool
        try:
            result = execute_tool(tool_name, tool_args)
            return json.dumps(result, indent=2) if isinstance(result, dict) else str(result)
        except Exception as e:
            return json.dumps({"error": f"Tool execution failed: {str(e)}"})
    
    
    def get_summary(self) -> str:
        """Get a summary of the reasoning trajectory."""
        lines = [f"Total steps: {len(self.steps)}"]
        for step in self.steps:
            lines.append(f"\nStep {step.step_num}:")
            lines.append(f"  Thought: {step.thought[:100]}...")
            if step.action:
                lines.append(f"  Action: {step.action.get('tool', 'unknown')}")
            if step.answer:
                lines.append(f"  Answer: {step.answer}")
        
        return "\n".join(lines)
