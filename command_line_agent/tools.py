import subprocess
from agents import function_tool

@function_tool
def execute_bash_command(command: str) -> str:
    """
    Executes a bash command and returns the output.
    """
    print(f"\n\nRunning bash command: {command}\n\n")
    try:
        # Using shell=True to allow complex commands (pipes, redirects, etc.)
        # Note: In a production environment, this requires strict sanitation.
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error executing command: {e.stderr.strip()}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

@function_tool
def run_powershell(code: str) -> str:
    """Runs PowerShell code and returns the output."""

    print(f"\n\nRunning PowerShell command: {code}\n\n")
    
    process = subprocess.Popen(
        ["powershell", "-Command", code],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    output, error = process.communicate()

    if process.returncode != 0:
        return f"Error: {error}"

    return output
