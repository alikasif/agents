import re
import unicodedata
from typing import Optional

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

