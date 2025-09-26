
import os
from crew import BloggerCrew

# Create output directory if it doesn't exist
os.makedirs('output', exist_ok=True)

def read_content() -> str:
    """Read the topic.txt file and return its content as a string."""
    with open("./ai_blogger/topic.txt", "r", encoding="utf-8") as f:
        return f.read()

def run():
    """
    Run the research crew.
    """
    inputs = {
        'topic': 'Evaluation of LLM and LLM based Applications',
        'content': read_content(),
        'file_path': './ai_blogger/crew_ai/output/outline.md',
        'output_file': './ai_blogger/crew_ai/output/research.md'
    }

    # Create and run the crew
    result = BloggerCrew().crew().kickoff(inputs=inputs)

    # Print the result
    print("\n\n=== FINAL REPORT ===\n\n")
    print(result.raw)

    print("\n\nReport has been saved to output/report.md")

if __name__ == "__main__":
    run()