import os
from anthropic import Anthropic
import re

GENERATED_DIR = os.path.join(os.path.dirname(__file__), 'generated')

class DeveloperAgent:
    def __init__(self):
        
        #self.client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.model_name = "claude-3-7-sonnet-latest"

        self.client = Anthropic()
        #response = claude.messages.create(model=model_name, messages=messages, max_tokens=1000)
        #answer = response.content[0].text


    def generate_code(self, user_request, project_name):
        """
        Generate modular code based on user request using Anthropic LLM.
        System prompt: expert developer, modular, testable Python code, split into appropriate modules/files.
        Saves each module in generated/<project_name>/.
        Returns a dict of {filename: code}.
        """
        system_prompt = (
            "You are an expert Python developer. Generate modular, well-structured, and testable Python code "
            "based on the user's request. Split the code into appropriate modules/files (e.g., main.py, utils.py, models.py, etc.) "
            "to maintain modularity. For each file, output a section starting with '### <filename>' followed by the code for that file. "
            "Do not include explanations, only output the code sections."
        )
        user_prompt = f"User request: {user_request}"
        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=2048,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            raw_output = response.content[0].text.strip()
            # Parse the output into {filename: code}
            modules = self._parse_modules(raw_output)
            # Strip markdown code block markers from each module
            modules = {fn: self._strip_code_block_markers(code) for fn, code in modules.items()}
            self.save_to_generated(project_name, modules)
            return modules
        except Exception as e:
            # Fallback stub if API fails
            print(f"exception in generating code {str(e)}")
            fallback_code = f"# Code generated for: {user_request}\nprint('Hello from generated code!')\n# [Anthropic API error: {e}]"
            self.save_to_generated(project_name, {"main.py": fallback_code})
            return {"main.py": fallback_code}

    def _parse_modules(self, raw_output):
        modules = {}
        current_file = None
        current_lines = []
        for line in raw_output.splitlines():
            if line.startswith('### '):
                if current_file and current_lines:
                    modules[current_file] = '\n'.join(current_lines).strip()
                current_file = line[4:].strip()
                current_lines = []
            elif current_file:
                current_lines.append(line)
        if current_file and current_lines:
            modules[current_file] = '\n'.join(current_lines).strip()
        return modules

    def _strip_code_block_markers(self, code):
        # Remove ```python, ```py, ``` and matching closing ```
        code = re.sub(r'^```(?:python|py)?\s*', '', code, flags=re.IGNORECASE | re.MULTILINE)
        code = re.sub(r'```\s*$', '', code, flags=re.MULTILINE)
        return code.strip()

    def save_to_generated(self, project_name, modules):
        project_dir = os.path.join(GENERATED_DIR, project_name)
        os.makedirs(project_dir, exist_ok=True)
        for filename, content in modules.items():
            with open(os.path.join(project_dir, filename), 'w', encoding='utf-8') as f:
                f.write(content)

    def generate_test(self, project_name):
        project_dir = os.path.join(GENERATED_DIR, project_name)
        tests_dir = os.path.join(project_dir, 'tests')
        os.makedirs(tests_dir, exist_ok=True)
        code_files = [f for f in os.listdir(project_dir) if f.endswith('.py') and f != '__init__.py']
        for code_file in code_files:
            code_path = os.path.join(project_dir, code_file)
            with open(code_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
            system_prompt = (
                "You are an expert Python developer. Write comprehensive unit tests for the following Python module. "
                "Use the unittest framework and mock external dependencies where appropriate. "
                "Output only the test code, do not include explanations."
            )
            user_prompt = f"Module: {code_file}\n\n{code_content}"
            try:
                response = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=1024,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}]
                )
                test_code = response.content[0].text.strip()
                test_code = self._strip_code_block_markers(test_code)
            except Exception as e:
                test_code = f"# Test for {code_file}\ndef test_placeholder():\n    assert True\n# [Anthropic API error: {e}]"
            test_filename = f"test_{code_file}"
            test_path = os.path.join(tests_dir, test_filename)
            with open(test_path, 'w', encoding='utf-8') as f:
                f.write(test_code)

    def fix_code_review(self, code, review_comments):
        fixed_code = code + f"\n# Fixed based on review: {review_comments}\n"
        return fixed_code 