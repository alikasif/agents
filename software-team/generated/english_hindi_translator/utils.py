"""
Utility functions for the translator
"""
import os
import logging
from typing import List

# Configure logging
def setup_logging(verbose=False):
    """Set up and return logger with appropriate level"""
    logger = logging.getLogger('translator')
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    return logger

def validate_file(file_path: str) -> bool:
    """
    Validate if a file exists and is readable
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        True if file exists and is readable, False otherwise
    """
    return os.path.isfile(file_path) and os.access(file_path, os.R_OK)

def read_file(file_path: str) -> str:
    """
    Read text from a file
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        Text content of the file
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def write_file(file_path: str, content: str) -> None:
    """
    Write text to a file
    
    Args:
        file_path: Path to the file to write
        content: Text content to write to the file
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def chunk_text(text: str, max_chunk_size: int = 5000) -> List[str]:
    """
    Split text into chunks for API processing
    
    Args:
        text: Text to split into chunks
        max_chunk_size: Maximum size of each chunk
        
    Returns:
        List of text chunks
    """
    # If text is shorter than max size, return as single chunk
    if len(text) <= max_chunk_size:
        return [text]
    
    chunks = []
    current_pos = 0
    
    while current_pos < len(text):
        # Find a good break point (end of sentence)
        end_pos = min(current_pos + max_chunk_size, len(text))
        
        # If we're not at the end, try to find a sentence break
        if end_pos < len(text):
            # Look for sentence endings within the last 100 chars of the chunk
            search_start = max(end_pos - 100, current_pos)
            
            # Find the last sentence ending in our search range
            last_period = text.rfind('. ', search_start, end_pos)
            last_newline = text.rfind('\n', search_start, end_pos)
            
            # Use the latest sentence ending found
            if last_period > current_pos:
                end_