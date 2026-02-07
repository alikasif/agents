import re
import unicodedata
from typing import Optional
import json

def current_date_str() -> str:
    """Return the current date as a string in yyyy-mm-dd format."""
    from datetime import date
    return date.today().isoformat()

