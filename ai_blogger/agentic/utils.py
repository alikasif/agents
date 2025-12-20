import re
import unicodedata
from typing import Optional
import json

def filename_from_input(text: str, max_length: Optional[int] = None) -> str:
    """Convert arbitrary user input into a safe filename string.

    - Lowercase
    - Remove diacritics
    - Replace non-alphanumeric with underscores
    - Collapse multiple underscores
    - Strip leading/trailing underscores
    - Fallback to 'file' if empty
    - Optionally truncate
    """
    if text is None:
        return "file"
    nfkd = unicodedata.normalize("NFKD", text)
    without_diacritics = "".join(c for c in nfkd if not unicodedata.combining(c))
    s = without_diacritics.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = s.strip("_")
    if not s:
        s = "file"
    if max_length is not None and max_length > 0 and len(s) > max_length:
        parts = s.split("_")
        truncated = []
        cur_len = 0
        for p in parts:
            add_len = len(p) + (1 if truncated else 0)
            if cur_len + add_len > max_length:
                break
            truncated.append(p)
            cur_len += add_len
        if not truncated:
            s = s[:max_length]
        else:
            s = "_".join(truncated)
    return s

def current_date_str() -> str:
    """Return the current date as a string in yyyy-mm-dd format."""
    from datetime import date
    return date.today().isoformat()


def load_completed_topics(progress_file_name: str) -> set:
    """Load the set of completed topic names from the progress file."""
    try:
        with open(progress_file_name, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data.get("completed_topics", []))
    except FileNotFoundError:
        return set()
    except json.JSONDecodeError:
        print(f"Warning: Could not parse progress file {progress_file_name}. Starting fresh.")
        return set()


def save_completed_topic(progress_file_name: str, topic_name: str):
    """Add a topic to the completed list and save to the progress file."""
    completed = load_completed_topics(progress_file_name)
    completed.add(topic_name)
    
    with open(progress_file_name, "w", encoding="utf-8") as f:
        json.dump({"completed_topics": list(completed)}, f, indent=2)
    print(f"Progress saved: '{topic_name}' marked as completed.")


def read_blog(blog_file_path: str):
    """Read the specified blog markdown file and return its content as a string."""
    with open(blog_file_path, "r") as f:
        return f.read()


def read_topic(topic_file_path: str):
    """Read the topic.txt file and return its content as a string."""
    with open(topic_file_path, "r", encoding="utf-8") as f:
        return f.read()
