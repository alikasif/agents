#!/usr/bin/env python3
"""
English to Hindi text file translator
"""
import argparse
import os
from translation import translate_file
from utils import setup_logging, validate_file

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Translate English text file to Hindi')
    parser.add_argument('-i', '--input', required=True, help='Input English text file path')
    parser.add_argument('-o', '--output', help='Output Hindi text file path')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')
    return parser.parse_args()

def main():
    """Main execution function"""
    args = parse_arguments()
    logger = setup_logging(args.verbose)
    
    # Validate input file
    if not validate_file(args.input):
        logger.error(f"Input file does not exist or is not readable: {args.input}")
        return 1
        
    # Set default output file if not provided
    output_file = args.output
    if not output_file:
        base_name = os.path.splitext(args.input)[0]
        output_file = f"{base_name}_hindi.txt"
    
    logger.info(f"Translating {args.input} to {output_file}")
    
    # Perform translation
    try:
        translate_file(args.input, output_file)
        logger.info("Translation completed successfully")
        return 0
    except Exception as e:
        logger.error(f"Translation failed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())
# Fixed based on review: 
Code execution failed. Please fix the following issues:

Command used: ..\ .venv\Scripts\activate && uv run generated/english_hindi_translator/main.py -i INPUT_FILE.txt -o OUTPUT_FILE.txt
Error: '..\' is not recognized as an internal or external command,
operable program or batch file.

Output: 

Please analyze the code and fix the issues that are preventing successful execution.


# Fixed based on review: 
Code execution failed. Please fix the following issues:

Command used: ..\ .venv\Scripts\activate && uv run generated/english_hindi_translator/main.py -i INPUT_FILE.txt -o OUTPUT_FILE.txt
Error: '..\' is not recognized as an internal or external command,
operable program or batch file.

Output: 

Please analyze the code and fix the issues that are preventing successful execution.


# Fixed based on review: 
Code execution failed. Please fix the following issues:

Command used: ..\ .venv\Scripts\activate && uv run generated/english_hindi_translator/main.py -i INPUT_FILE.txt -o OUTPUT_FILE.txt
Error: '..\' is not recognized as an internal or external command,
operable program or batch file.

Output: 

Please analyze the code and fix the issues that are preventing successful execution.

