"""
Translation module for English to Hindi conversion
"""
import os
from typing import List
import requests
from utils import read_file, write_file, chunk_text, setup_logging

logger = setup_logging()

# You can replace this with your preferred translation API
TRANSLATION_API_URL = "https://translation.googleapis.com/language/translate/v2"
# You would need to set up your API key in environment variables
API_KEY = os.environ.get("GOOGLE_TRANSLATE_API_KEY", "")

def translate_text(text: str) -> str:
    """
    Translate English text to Hindi using translation API
    
    Args:
        text: The English text to translate
        
    Returns:
        The translated Hindi text
    """
    logger.debug(f"Translating text of length: {len(text)}")
    
    # If API key is not set, use alternative translation method
    if not API_KEY:
        try:
            from googletrans import Translator
            translator = Translator()
            result = translator.translate(text, src='en', dest='hi')
            return result.text
        except ImportError:
            logger.warning("googletrans not installed, falling back to API translation")
            logger.warning("Install with: pip install googletrans==4.0.0-rc1")
            # Continue with API approach, but it will likely fail without a key

    # Using Google Cloud Translation API
    params = {
        'q': text,
        'source': 'en',
        'target': 'hi',
        'key': API_KEY
    }
    
    try:
        response = requests.post(TRANSLATION_API_URL, params=params)
        response.raise_for_status()
        return response.json()['data']['translations'][0]['translatedText']
    except requests.exceptions.RequestException as e:
        logger.error(f"Translation API error: {e}")
        raise

def translate_chunks(chunks: List[str]) -> List[str]:
    """
    Translate a list of text chunks from English to Hindi
    
    Args:
        chunks: List of English text chunks
        
    Returns:
        List of translated Hindi text chunks
    """
    translated_chunks = []
    total_chunks = len(chunks)
    
    for i, chunk in enumerate(chunks):
        logger.info(f"Translating chunk {i+1}/{total_chunks}")
        translated_chunk = translate_text(chunk)
        translated_chunks.append(translated_chunk)
    
    return translated_chunks

def translate_file(input_file: str, output_file: str) -> None:
    """
    Translate English text file to Hindi and save to output file
    
    Args:
        input_file: Path to English text file
        output_file: Path to save Hindi translation
    """
    # Read input file
    english_text = read_file(input_file)
    logger.info(f"Read {len(english_text)} characters from {input_file}")
    
    # Split into manageable chunks (for API limits)
    chunks = chunk_text(english_text)
    logger.info(f"Split into {len(chunks)} chunks for translation")
    
    # Translate chunks
    hindi_chunks = translate_chunks(chunks)
    
    # Combine and write to output file
    hindi_text = ''.join(hindi_chunks)
    write_file(output_file, hindi_text)
    logger.info(f"Wrote {len(hindi_text)} characters to {output_file}")