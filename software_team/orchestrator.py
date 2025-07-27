from agent_developer import DeveloperAgent
from agent_code_review import CodeReviewAgent
from agent_github import GitHubIntegrationAgent
from agent_tester import TesterAgent
import os
from dotenv import load_dotenv


GENERATED_DIR = os.path.join(os.path.dirname(__file__), 'generated')

def run_developer_agent_only():
    dev_agent = DeveloperAgent()
    user_request = input('Describe the feature or code you want to generate: ')
    project_name = input('Enter a project name: ')
    project_dir = os.path.join(GENERATED_DIR, project_name)
    if os.path.exists(project_dir):
        print(f"Project '{project_name}' already exists. Skipping code and test generation.")
        return
    # Step 1: Generate code
    modules = dev_agent.generate_code(user_request, project_name)
    print(f'Code modules generated for project "{project_name}":')
    for filename in modules:
        print(f'  - {filename}')
    # Step 2: Generate tests
    dev_agent.generate_test(project_name)
    print(f'Unit tests generated under generated/{project_name}/tests/')

def run_code_review_only():
    review_agent = CodeReviewAgent()
    project_name = input('Enter the project name to review: ')
    project_dir = os.path.join(GENERATED_DIR, project_name)
    if not os.path.exists(project_dir):
        print(f"Project '{project_name}' does not exist in generated/.")
        return
    review_results = review_agent.review_code(project_name)
    print("\nCode review results:")
    for module, comments in review_results.items():
        print(f"\n--- {module} ---\n{comments}")

def run_with_testing():
    dev_agent = DeveloperAgent()
    tester_agent = TesterAgent()
    user_request = input('Describe the feature or code you want to generate: ')
    project_name = input('Enter a project name: ')
    project_dir = os.path.join(GENERATED_DIR, project_name)
    if os.path.exists(project_dir):
        print(f"Project '{project_name}' already exists. Skipping code and test generation.")
    else:
        # Step 1: Generate code
        modules = dev_agent.generate_code(user_request, project_name)
        print(f'Code modules generated for project "{project_name}":')
        for filename in modules:
            print(f'  - {filename}')
        # Step 2: Generate tests
        dev_agent.generate_test(project_name)
        print(f'Unit tests generated under generated/{project_name}/tests/')
    # Step 3: Test the generated code with feedback loop
    test_success, iterations = tester_agent.test_project(project_name, developer_agent=dev_agent)
    if test_success:
        print(f"\n✅ Project '{project_name}' passed all tests after {iterations} iterations!")
    else:
        print(f"\n❌ Project '{project_name}' failed after {iterations} iterations.")

def main():
    dev_agent = DeveloperAgent()
    review_agent = CodeReviewAgent()
    github_agent = GitHubIntegrationAgent()
    tester_agent = TesterAgent()

    user_request = input('Describe the feature or code you want to generate: ')
    project_name = input('Enter a project name: ')
    project_dir = os.path.join(GENERATED_DIR, project_name)
    if os.path.exists(project_dir):
        print(f"Project '{project_name}' already exists. Skipping code and test generation.")
    else:
        # Step 1: Generate code
        modules = dev_agent.generate_code(user_request, project_name)
        print(f'Code modules generated for project "{project_name}":')
        for filename in modules:
            print(f'  - {filename}')
        # Step 2: Generate test
        dev_agent.generate_test(project_name)
        print(f'Unit tests generated under generated/{project_name}/tests/')
    # Step 3: Test the generated code with feedback loop
    test_success, iterations = tester_agent.test_project(project_name, developer_agent=dev_agent)
    # Step 4: Code review (stub: review only main.py and its test)
    main_code = None
    test_code = ''
    main_path = os.path.join(project_dir, 'main.py')
    if os.path.exists(main_path):
        with open(main_path, 'r', encoding='utf-8') as f:
            main_code = f.read()
    test_path = os.path.join(project_dir, 'tests', 'test_main.py')
    if os.path.exists(test_path):
        with open(test_path, 'r', encoding='utf-8') as f:
            test_code = f.read()
    if main_code is not None:
        approved, comments = review_agent.review_code(main_code, test_code)
        print(f'Code review comments: {comments}')
        # Step 5: Fixes & resubmission if needed
        if not approved:
            fixed_code = dev_agent.fix_code_review(main_code, comments)
            dev_agent.save_to_generated(project_name, {'main.py': fixed_code})
            print('Code fixed and resubmitted.')
            approved, comments = review_agent.review_code(fixed_code, test_code)
            print(f'Code review comments after fix: {comments}')
        # Step 6: Commit if approved
        if approved:
            github_agent.commit_and_push([os.path.join(project_name, 'main.py'), os.path.join(project_name, 'tests', 'test_main.py')])
        else:
            print('Code not approved. Please review and try again.')
    else:
        print('No main.py found to review.')

if __name__ == '__main__':
    load_dotenv(override=True)
    # main()
    # run_developer_agent_only()
    # run_with_testing()
    run_code_review_only() 