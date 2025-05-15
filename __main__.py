from pdf_reader import extract_text
from transform import *
from speaker import speak_file
from preprocessor import preprocess_file
from argparse import ArgumentParser

from typing import Optional


def main(path: str, max_length: int = -1) -> None:
    """
    Main function to process a PDF file, extract its text, transform it, and save the result.
    
    Args:
        path (str): The path to the PDF file.
    
    Returns:
        None
    """
    text = extract_text(path)
    list_of_files = transform(text, max_length_book_as_single_file=max_length)
    
    for file in list_of_files: 
        preprocessed_file = preprocess_file(file)
        speak_file(preprocessed_file)
        

if __name__ == "__main__":
    """
    Args: 
        path (str): The path to the PDF file.
        max_length (int): The maximum length of the text to process. Only relevant if the Table of Contents can not be extracted.
    Returns:
        None 
    """
    parser = ArgumentParser(description="Process a PDF file and extract its text.")
    parser.add_argument("path", required=True, type=str, help="The path to the PDF file.")
    parser.add_argument("--max_length", type=int, default=-1, help="The maximum length of the text to process. Only relevant if the Table of Contents can not be extracted.")

    args = parser.parse_args()
    
    main(args.path, args.max_length)
