import os
import subprocess
import sys
import importlib.util
import ast
import re
from pathlib import Path
import openai

GENERATED_DIR = os.path.join(os.path.dirname(__file__), 'generated')

class TesterAgent:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def analyze_and_get_execution_command(self, project_name, code_content):
        """
        Use LLM to analyze the code and determine appropriate command line execution using 'uv' and the virtual environment.
        Returns the command to execute the code.
        """
        system_prompt = (
            "You are an expert software tester and execution specialist. Analyze the provided Python code and determine "
            "the appropriate command line to execute it using the 'uv' tool and the project's virtual environment. Consider:\n"
            "1. What the code is trying to accomplish\n"
            "2. What inputs or arguments it might need\n"
            "3. What environment or dependencies it requires\n"
            "4. How to handle interactive inputs\n"
            "5. Always use the 'uv' tool for execution and ensure the command uses the project's virtual environment is activated before execution (e.g., 'uv', 'uv run ...')\n\n"
            "Return ONLY the command line that should be used to execute the code. "
            "If the code needs input, provide the input in the command or specify how to provide it. "
            "Do not include explanations, just the command."
        )
        
        user_prompt = f"""
Analyze this Python code and provide the command line to execute it using 'uv':

{code_content}

Project name: {project_name}
File location: generated/{project_name}/main.py

Assume the virtual environment is already created with 'uv venv .venv' and dependencies are installed. Provide the command line to activate the virtual environment using ..\\.venv\\Scripts\\activate and  execute this code using 'uv run':
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            command = response.choices[0].message.content.strip()
            print(f"execution command :: {command}")
            return command
        except Exception as e:
            return f"uv run python main.py"

    def execute_with_command(self, project_name, command):
        """
        Execute the code using the provided command.
        Returns a tuple: (success: bool, output: str, error: str)
        """
        #project_dir = os.path.join(GENERATED_DIR, project_name)
        project_dir = os.path.dirname(__file__)
        
        if not os.path.exists(project_dir):
            return False, "", f"Project directory not found: {project_dir}"
        
        try:
            # Change to project directory
            original_cwd = os.getcwd()
            os.chdir(project_dir)

            print(f"current working dir :: {os.getcwd()}")
            
            # Execute the command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            os.chdir(original_cwd)
            
            success = result.returncode == 0
            return success, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            os.chdir(original_cwd)
            return False, "", "Program execution timed out after 30 seconds"
        except Exception as e:
            os.chdir(original_cwd)
            return False, "", f"Error executing command '{command}': {str(e)}"

    def get_execution_context(self, project_name, command, success, output, error):
        """
        Create execution context for DeveloperAgent to understand what went wrong.
        """
        project_dir = os.path.join(GENERATED_DIR, project_name)
        main_file = os.path.join(project_dir, 'main.py')
        
        context = {
            'project_name': project_name,
            'command_used': command,
            'execution_success': success,
            'output': output,
            'error': error,
            'file_exists': os.path.exists(main_file),
            'working_directory': project_dir
        }
        
        # Add file content if available
        if os.path.exists(main_file):
            try:
                with open(main_file, 'r', encoding='utf-8') as f:
                    context['code_content'] = f.read()
            except Exception as e:
                context['code_content'] = f"Error reading file: {str(e)}"
        
        return context

    def test_project_with_feedback_loop(self, project_name, developer_agent, max_iterations=3):
        """
        Test the project with a feedback loop to DeveloperAgent.
        Returns: (final_success: bool, iterations: int)
        """
        print(f"\n=== Testing Project: {project_name} ===")
        
        project_dir = os.path.join(GENERATED_DIR, project_name)
        main_file = os.path.join(project_dir, 'main.py')
        
        if not os.path.exists(main_file):
            print(f"❌ main.py not found in {project_dir}")
            return False, 0
        
        # Read the code content
        with open(main_file, 'r', encoding='utf-8') as f:
            code_content = f.read()
        
        for iteration in range(1, max_iterations + 1):
            print(f"\n🔄 Iteration {iteration}/{max_iterations}")
            
            # Step 1: Get execution command from LLM
            print("1. Analyzing code and getting execution command...")
            command = self.analyze_and_get_execution_command(project_name, code_content)
            print(f"Command: {command}")
            
            # Step 2: Execute the code
            print("2. Executing code...")
            success, output, error = self.execute_with_command(project_name, command)
            
            if success:
                print("✅ Code executed successfully!")
                if output.strip():
                    print(f"Output: {output}")
                return True, iteration
            else:
                print("❌ Code execution failed!")
                if error:
                    print(f"Error: {error}")
                
                # Step 3: Get execution context and ask DeveloperAgent to fix
                print("3. Getting execution context and asking DeveloperAgent to fix...")
                context = self.get_execution_context(project_name, command, success, output, error)
                
                # Create feedback message for DeveloperAgent
                feedback = f"""
Code execution failed. Please fix the following issues:

Command used: {context['command_used']}
Error: {context['error']}
Output: {context['output']}

Please analyze the code and fix the issues that are preventing successful execution.
"""
                
                # Ask DeveloperAgent to fix the code
                fixed_code = developer_agent.fix_code_review(code_content, feedback)
                developer_agent.save_to_generated(project_name, {'main.py': fixed_code})
                
                # Update code content for next iteration
                code_content = fixed_code
                print("Code fixed and saved. Will retry execution...")
        
        print(f"\n❌ Failed to get working code after {max_iterations} iterations.")
        return False, max_iterations

    def run_unit_tests(self, project_name):
        """
        Run unit tests for the project.
        Returns a tuple: (success: bool, output: str, error: str)
        """
        project_dir = os.path.join(GENERATED_DIR, project_name)
        tests_dir = os.path.join(project_dir, 'tests')
        
        if not os.path.exists(tests_dir):
            return False, "", f"tests directory not found in {project_dir}"
        
        try:
            # Change to project directory
            original_cwd = os.getcwd()
            os.chdir(project_dir)
            
            # Run tests using unittest discovery
            result = subprocess.run(
                [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_*.py'],
                capture_output=True,
                text=True,
                timeout=60  # 60 second timeout for tests
            )
            
            os.chdir(original_cwd)
            
            success = result.returncode == 0
            return success, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            os.chdir(original_cwd)
            return False, "", "Unit tests timed out after 60 seconds"
        except Exception as e:
            os.chdir(original_cwd)
            return False, "", f"Error running unit tests: {str(e)}"

    def test_project(self, project_name, developer_agent=None):
        """
        Comprehensive testing of the generated project.
        If developer_agent is provided, uses feedback loop. Otherwise, just tests.
        """
        if developer_agent:
            return self.test_project_with_feedback_loop(project_name, developer_agent)
        else:
            # Simple test without feedback loop
            print(f"\n=== Testing Project: {project_name} ===")
            
            # Get execution command
            project_dir = os.path.join(GENERATED_DIR, project_name)
            main_file = os.path.join(project_dir, 'main.py')
            
            if not os.path.exists(main_file):
                print(f"❌ main.py not found in {project_dir}")
                return False, "main.py not found"
            
            with open(main_file, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            command = self.analyze_and_get_execution_command(project_name, code_content)
            print(f"Command: {command}")
            
            success, output, error = self.execute_with_command(project_name, command)
            
            if success:
                print("✅ Code executed successfully!")
                return True, "Success"
            else:
                print("❌ Code execution failed!")
                return False, f"Error: {error}" 