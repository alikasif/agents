import os
from openai import OpenAI

from datetime import datetime

GENERATED_DIR = os.path.join(os.path.dirname(__file__), 'generated')

class CodeReviewAgent:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def review_code(self, project_name):
        """
        Review all code modules in generated/{project_name}/ using OpenAI LLM.
        Save code review comments in code_review_{timestamp}.md under generated/{project_name}/code_review/.
        Output format: module_name, line number, review comment (as a markdown table).
        Returns a dict {module: [ (line_number, comment) ] }.
        """
        project_dir = os.path.join(GENERATED_DIR, project_name)
        code_review_dir = os.path.join(project_dir, 'code_review')
        os.makedirs(code_review_dir, exist_ok=True)
        modules = [f for f in os.listdir(project_dir) if f.endswith('.py')]
        review_results = {}
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        review_file_path = os.path.join(code_review_dir, f'code_review_{timestamp}.md')
        with open(review_file_path, 'w', encoding='utf-8') as review_file:
            review_file.write(f'# Code Review for {project_name} ({timestamp})\n\n')
            review_file.write('| Module | Line | Comment |\n')
            review_file.write('|--------|------|---------|\n')
            for module in modules:
                module_path = os.path.join(project_dir, module)
                with open(module_path, 'r', encoding='utf-8') as f:
                    code_content = f.read()
                system_prompt = (
                    "You are an expert Python code reviewer. Carefully review the following Python module. "
                    "For each issue or suggestion, output your feedback in the following format: "
                    "module_name, line number, review comment. "
                    "If the code is good, say so for the relevant lines, but still suggest any possible improvements. "
                    "If you have general comments, use line number 0. "
                    "Example: main.py, 12, Use a context manager for file operations."
                )
                user_prompt = f"Module: {module}\n\n{code_content}"
                try:
                    response = self.client.chat.completions.create(
                        model="gpt-4.1",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        max_tokens=1200,
                        temperature=0.2
                    )
                    review_comments = response.choices[0].message.content.strip()
                except Exception as e:
                    review_comments = f"Error during code review: {str(e)}"
                # Parse and store structured review comments
                parsed_comments = []
                for line in review_comments.splitlines():
                    if not line.strip():
                        continue
                    # Try to parse: module_name, line_number, comment
                    parts = line.split(',', 2)
                    if len(parts) == 3:
                        mod, line_num, comment = parts
                        parsed_comments.append((mod.strip(), line_num.strip(), comment.strip()))
                        review_file.write(f'| {mod.strip()} | {line_num.strip()} | {comment.strip()} |\n')
                    else:
                        # fallback: just write the line as a comment with line 0
                        review_file.write(f'| {module} | 0 | {line.strip()} |\n')
                review_results[module] = parsed_comments
        print(f"Code review comments saved to {review_file_path}")
        return review_results 