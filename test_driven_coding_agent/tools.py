"""
TDD Agent Tools

Tools for test generation, execution, and code implementation.
"""

import subprocess
import os
import logging
from agents import function_tool
from litellm import completion
from prompts import TEST_GEN_PROMPT, IMPL_GEN_PROMPT

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

FLASH_MODEL= os.getenv("GEMINI3_FLASH_MODEL", "gemini/gemini-2.0-flash")


def _call_llm(system_prompt: str, user_prompt: str) -> str:
    """Call LLM and extract code from response."""
    logger.info("Calling LLM...")
    response = completion(
        model=FLASH_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2
    )
    content = response.choices[0].message.content
    logger.info(f"LLM response received ({len(content)} chars)")
    
    if "```python" in content:
        content = content.split("```python")[1].split("```")[0]
    elif "```" in content:
        content = content.split("```")[1].split("```")[0]
    
    return content.strip()


@function_tool
def generate_tests(problem: str) -> str:
    """
    Generate pytest test cases from a problem description.
    
    Args:
        problem: Natural language description of the problem to solve
        
    Returns:
        Python code string containing pytest tests
    """
    logger.info("=" * 50)
    logger.info("GENERATE_TESTS called")
    logger.info(f"Problem: {problem[:100]}...")
    
    user_prompt = f"Generate tests for this problem:\n\n{problem}"
    tests = _call_llm(TEST_GEN_PROMPT, user_prompt)
    
    logger.info(f"Generated {tests.count('def test_')} test functions")
    logger.info("=" * 50)
    return tests


# Module-level run directory tracker
_current_run_dir = None


def _get_run_dir() -> str:
    """Get or create the current run directory."""
    global _current_run_dir
    if _current_run_dir is None:
        from datetime import datetime
        project_dir = os.path.dirname(os.path.abspath(__file__))
        runs_dir = os.path.join(project_dir, "runs")
        os.makedirs(runs_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        _current_run_dir = os.path.join(runs_dir, f"run_{timestamp}")
        os.makedirs(_current_run_dir, exist_ok=True)
        logger.info(f"Created run directory: {_current_run_dir}")
    return _current_run_dir


@function_tool
def run_tests(test_code: str, impl_code: str) -> dict:
    """
    Execute pytest tests against implementation code.
    Saves code and tests in runs/<timestamp>/ folder for persistence.
    
    Args:
        test_code: Python test code to execute
        impl_code: Python implementation code to test
        
    Returns:
        Dictionary with passed (bool), output (str), and run_dir path
    """
    logger.info("=" * 50)
    logger.info("RUN_TESTS called")
    
    work_dir = _get_run_dir()
    test_file = os.path.join(work_dir, "test_solution.py")
    impl_file = os.path.join(work_dir, "solution.py")
    
    logger.info(f"Writing test_solution.py ({len(test_code)} chars)")
    with open(test_file, "w") as f:
        f.write(test_code)
    
    logger.info(f"Writing solution.py ({len(impl_code)} chars)")
    with open(impl_file, "w") as f:
        f.write(impl_code)
    
    logger.info("Running pytest...")
    
    # Get project root (d:\GitHub\agents\test_driven_coding_agent)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to d:\GitHub\agents
    agents_dir = os.path.dirname(current_dir)
    venv_activate = os.path.join(agents_dir, ".venv", "Scripts", "activate.bat")
    
    output_file = os.path.join(work_dir, "test_output.txt")
    
    # Build command to activate venv and run pytest
    if os.path.exists(venv_activate):
        # Run in new window, capture output to file
        # /c closes window after done, /k keeps it open. User probably wants to see it?
        # But we need to know when it finishes.
        # We'll use /c and wait for the file to exist/process to finish.
        # Actually, to stream output to file AND show in window is hard in pure cmd.
        # We will run it in a new window and redirect to file.
        cmd = f'start /wait cmd /c "{venv_activate} && python -m pytest {test_file} -v --tb=short > {output_file} 2>&1"'
        logger.info(f"Using venv: {venv_activate}")
    else:
        # Fallback
        cmd = f'start /wait cmd /c "python -m pytest {test_file} -v --tb=short > {output_file} 2>&1"'
        logger.warning(f"No .venv found at {venv_activate}, using system Python")
    
    logger.info(f"Command: {cmd}")
    
    # Run the command
    subprocess.run(cmd, shell=True, check=True)
    
    # Read the output from file
    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            output = f.read()
    else:
        output = "Error: Test output file was not created."
    
    # Determine pass/fail from output content since we can't easily get return code from start /wait
    passed = "no tests ran" not in output and "failed" not in output and "Error" not in output and "ERRORS" not in output
    # Pytest usually says "X passed, Y failed" or "== 1 failed, 2 passed =="
    # A robust check: look for "failed" in the summary line at the bottom
    # But easier: check if "FAILED" appears in the output at all? No, "FAILED" appears in logic too.
    # Pytest exit code is best but 'start' swallows it.
    # Let's rely on string parsing for now.
    passed = "== 1 failed" not in output and " failed," not in output and "ERRORS" not in output
    if "passed" in output and "failed" not in output:
         passed = True
    elif "failed" in output:
         passed = False
    
    # Re-verify based on standard pytest output line e.g. "== 1 passed in 0.01s =="
    lines = output.strip().split('\n')
    last_line = lines[-1] if lines else ""
    if "failed" in last_line or "error" in last_line:
        passed = False
    elif "passed" in last_line:
        passed = True
    
    if passed:
        logger.info("✓ ALL TESTS PASSED")
    else:
        logger.warning("✗ TESTS FAILED")
        # Log first few lines of error
        error_lines = [l for l in output.split('\n') if 'FAILED' in l or 'ERROR' in l]
        for line in error_lines[:5]:
            logger.warning(f"  {line}")
    
    logger.info("=" * 50)
    return {
        "passed": passed,
        "output": output[:3000],
        "run_dir": work_dir
    }


@function_tool
def generate_implementation(problem: str, tests: str, error_output: str = "") -> str:
    """
    Generate implementation code to pass the given tests.
    
    Args:
        problem: Original problem description
        tests: The pytest test code that must pass
        error_output: Error output from last test run (if any)
        
    Returns:
        Python code string with the implementation
    """
    logger.info("=" * 50)
    logger.info("GENERATE_IMPLEMENTATION called")
    if error_output:
        logger.info("Fixing implementation based on error output")
    else:
        logger.info("Generating initial implementation")
    
    user_prompt = f"""Problem:
{problem}

Tests to pass:
```python
{tests}
```"""
    
    if error_output:
        user_prompt += f"""

Last test run output:
```
{error_output[:2000]}
```
Fix the implementation to pass all tests."""

    impl = _call_llm(IMPL_GEN_PROMPT, user_prompt)
    logger.info(f"Generated implementation ({len(impl)} chars)")
    
    # Parse implementation for multiple files
    # Format expected:
    # # filename: models.py
    # ... code ...
    # # filename: utils.py
    # ... code ...
    
    work_dir = _get_run_dir()
    
    # Split by filename markers
    import re
    # Regex to find "# filename: <name>" and capture name and content
    # This split strategy is tricky because split removes delimiters.
    # Better to iterate lines.
    
    current_file = "solution.py" # Default if no marker found
    file_content = []
    files_created = []
    
    lines = impl.split('\n')
    for line in lines:
        match = re.match(r'^#\s*filename:\s*(.+)$', line.strip(), re.IGNORECASE)
        if match:
            # Save previous file if it has content
            if file_content:
                full_path = os.path.join(work_dir, current_file)
                with open(full_path, "w") as f:
                    f.write('\n'.join(file_content))
                files_created.append(current_file)
                logger.info(f"Created {current_file} ({len(file_content)} lines)")
                file_content = []
            
            # Start new file
            current_file = match.group(1).strip()
        else:
            file_content.append(line)
            
    # Save last file
    if file_content:
        full_path = os.path.join(work_dir, current_file)
        with open(full_path, "w") as f:
            f.write('\n'.join(file_content))
        files_created.append(current_file)
        logger.info(f"Created {current_file} ({len(file_content)} lines)")
    
    logger.info("=" * 50)
    
    # Return the provided implementation text just for the record, 
    # but the files are what matters.
    return impl
