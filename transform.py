from typing import Optional


def transform(book: str, max_length_book_as_single_file=10000) -> list: 
    """ 
    Transform the book into a table of contents. 
    """
    toc = extract_table_of_contents_txt(book)
    
    if toc is None:
        if max_length_book_as_single_file < len(book):
            Exception("Table of contents not found and the book is too long to be processed as a single file.")

        print("Table of contents not found. Writing the book into a single file.")
        return [write_into_txt_file(book)]

        
    toc_json = transform_table_of_contents_into_json(toc)

    toc_enriched = enrich_table_of_contents_with_characters(book, toc_json)

    list_of_files = split_book_into_txt_files(book, toc_enriched)
    
    return list_of_files

def extract_table_of_contents_txt(book: str) -> Optional[str]:
    """
    Extract the table of contents from a book as a string. Raw text.
    If the table of contents is not found, return None.
    """
    if read_cache_table_of_contents(book) is not None:
        return read_cache_table_of_contents(book)
    
    #TODO: Implement the extraction logic
    toc = ""
    if False: #WEnn die Extraktion nicht erfolgreich ist
        print("Table of contents not found.")
        return None 

    print("Table of contents found.")
    write_extracted_table_of_contents_cache(book, toc)
    return toc

    


def transform_table_of_contents_into_json(book: str) -> list:
    """
    Transform the table of contents into a JSON object."
    
    Output format: 
    [
        {
            name: "Chapter 1 name", 
            page: 1,
            sub: [
                {
                    name: "Subchapter 1 name", 
                    page: 2,
                    sub: [
                        {name: "Subsubchapter 1 name", page: 3},
                        {name: "Subsubchapter 2 name", page: 4},
                    ]
                },
                {name: "Subchapter 2 name", page: 5},
            ]
        },
        {name: "Chapter 2 name", page: 12},
        {name: "Chapter 3 name", page: 15},
    ]
    """
    if read_cache_table_of_contents(book) is not None:
        return read_cache_table_of_contents(book)

    #TODO: Implement the transformation logic
    toc_json = []

    write_cache_table_of_contents(book, toc_json)
    return toc_json


def enrich_table_of_contents_with_characters(book: str, toc: dict) -> dict:
    """
    Enrich the table of contents with character number information.

    Output format: 
    [
        {
            name: "Chapter 1 name", 
            page: 1,
            character: 1123,
            sub: [
                {
                    name: "Subchapter 1 name", 
                    page: 2,
                    character: 2123,
                    sub: [
                        {name: "Subsubchapter 1 name", page: 3, character: 3123},
                        {name: "Subsubchapter 2 name", page: 4, character: 4123},
                    ]
                },
                {name: "Subchapter 2 name", page: 5, character: 5123},
            ]
        },
        {name: "Chapter 2 name", page: 12, character: 6123},
        {name: "Chapter 3 name", page: 15, character: 7123},
    ]
    """
    if read_cache_enriched_table_of_contents(book) is not None:
        return read_cache_enriched_table_of_contents(book)
    
    enriched_toc = toc #TODO: Implement the enrichment logic

    write_cache_enriched_table_of_contents(book, enriched_toc)
    return enriched_toc





def split_book_into_txt_files(book: str, enrichted_toc: dict) -> list:
    """
    Split the book into multiple text files.
    Each text file contains the smalles unit of the book and has its name from the toc.
    Every chapter can have a intro and a outro.
    Returns a list of the paths to the text files.

    """
    pass

def write_into_txt_file(book: str) -> str:
    """
    Write the book into a txt file.
    The file is named with the hash of the book.
    The file is located in the same directory as the book.
    """
    import os
    import hashlib

    # Get the hash of the book
    book_hash = hashlib.md5(book.encode()).hexdigest()
    cache_file = f"cache/{book_hash}/book.txt"

    # Create the cache directory if it does not exist
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)

    # Write the book to the cache file
    with open(cache_file, 'w') as file:
        file.write(book)

    return cache_file










def read_extracted_table_of_contents_cache(book: str) -> Optional[str]:
    """
    Read the extracted table of contents from a cache file.
    The cache file is named with the hash of the book.
    The cache file is located in the same directory as the book.
    If the cache file does not exist, return None.
    """
    import os
    import hashlib

    # Get the hash of the book
    book_hash = hashlib.md5(book.encode()).hexdigest()
    cache_file = f"cache/{book_hash}/toc.txt"

    # Check if the cache file exists
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as file:
            return file.read()
    
    return None

def write_extracted_table_of_contents_cache(book: str, toc: str) -> None:
    """
    Write the extracted table of contents to a cache file.
    The cache file is named with the hash of the book.
    The cache file is located in the same directory as the book.
    """
    import os
    import hashlib

    # Get the hash of the book
    book_hash = hashlib.md5(book.encode()).hexdigest()
    cache_file = f"cache/{book_hash}/toc.txt"

    # Create the cache directory if it does not exist
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)

    # Write the extracted table of contents to the cache file
    with open(cache_file, 'w') as file:
        file.write(toc)

def read_cache_enriched_table_of_contents(book: str) -> Optional[dict]:
    """
    Read the enriched table of contents from a cache file.
    The cache file is named with the hash of the book.
    The cache file is located in the same directory as the book.
    If the cache file does not exist, return None.
    """
    import os
    import hashlib
    import json

    # Get the hash of the book
    book_hash = hashlib.md5(book.encode()).hexdigest()
    cache_file = f"cache/{book_hash}/toc_enriched.json"

    # Check if the cache file exists
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as file:
            return json.load(file)
    
    return None

def write_cache_enriched_table_of_contents(book: str, toc: dict) -> None:
    """
    Write the enriched table of contents to a cache file.
    The cache file is named with the hash of the book.
    The cache file is located in the same directory as the book.
    """
    import os
    import hashlib
    import json

    # Get the hash of the book
    book_hash = hashlib.md5(book.encode()).hexdigest()
    cache_file = f"cache/{book_hash}/toc_enriched.json"

    # Create the cache directory if it does not exist
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)

    # Write the enriched table of contents to the cache file
    with open(cache_file, 'w') as file:
        json.dump(toc, file)


        
def read_cache_table_of_contents(book: str) -> Optional[dict]:
    """
    Read the table of contents from a cache file.
    The cache file is named with the hash of the book.
    The cache file is located in the same directory as the book.
    If the cache file does not exist, return None.
    """
    import os
    import hashlib
    import json

    # Get the hash of the book
    book_hash = hashlib.md5(book.encode()).hexdigest()
    cache_file = f"cache/{book_hash}/toc.json"

    # Check if the cache file exists
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as file:
            return json.load(file)
    
    return None

def write_cache_table_of_contents(book: str, toc: dict) -> None:
    """
    Write the table of contents to a cache file.
    The cache file is named with the hash of the book.
    The cache file is located in the same directory as the book.
    """
    import os
    import hashlib
    import json

    # Get the hash of the book
    book_hash = hashlib.md5(book.encode()).hexdigest()
    cache_file = f"cache/{book_hash}/toc.json"

    # Create the cache directory if it does not exist
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)

    # Write the table of contents to the cache file
    with open(cache_file, 'w') as file:
        json.dump(toc, file)