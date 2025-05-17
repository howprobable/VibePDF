from typing import Optional

from dotenv import load_dotenv

load_dotenv()

from gptLang import Funktion, Parameter
from fuzzywuzzy import fuzz

ASSUME_TOC_IN_FIRST_CHARACTERS = 10000
ASSUME_LARGEST_SUBSUBCHAPTER_LENGTH = 10000



def find_substring_with_tolerance(main_string, sub_string, tolerance=70):
        for i in range(len(main_string) - len(sub_string) + 1):
            substring = main_string[i:i + len(sub_string)]
            similarity = fuzz.partial_ratio(substring, sub_string)
            if similarity >= tolerance:
                return True, i, similarity
        return False, -1, 0


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
    
    toc_json = transform_table_of_contents_into_json(book, toc)

    toc_enriched = enrich_table_of_contents_with_characters(book, toc_json)

    list_of_files = split_book_into_txt_files(book, toc_enriched)
    
    return list_of_files


def extract_table_of_contents_txt(book: str) -> Optional[str]:
    """
    Extract the table of contents from a book as a string. Raw text.
    If the table of contents is not found, return None.
    """
    if read_extracted_table_of_contents_cache(book) is not None:
        print("Table of contents found in cache.")
        return read_extracted_table_of_contents_cache(book)
    else: 
        print("Table of contents not found in cache. Extracting it from the book.")
    
    toc = Funktion(
        returnType=Parameter(type=str, name="table_of_contents"),
        gpt_params={
            "max_interactions": 10,
            "max_function_iterations": 10
        },
        context=f"""
The user will give you a part of a pdf of a book. It will be the first {ASSUME_TOC_IN_FIRST_CHARACTERS} characters of the book.
Your task is to extract the table of contents from the book.
The table of contents is a list of chapters and subchapters with their page numbers.
Return the table of contentents in a human readable format.
If there is no table of contents, return an empty string.
If the table of contents contain page numbers, keep them. If it does not contain page numbers, no problem.
""",    
        inputPromptFormatString=f"{book[:ASSUME_TOC_IN_FIRST_CHARACTERS]}",
        model="gpt-4.1-2025-04-14",
        can_throw=False,
    )()

    if toc == "":
        print("Table of contents not found.")
        return None 

    print("Table of contents found.")
    write_extracted_table_of_contents_cache(book, toc)
    return toc


def transform_table_of_contents_into_json(book: str, toc: str) -> list:
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
        print("Table of contents JSON found in cache.")
        return read_cache_table_of_contents(book)
    else: 
        print("Table of contents JSON not found in cache. Transforming it into JSON.")

    toc_json = Funktion(
        returnType=Parameter(type=list[dict], name="table_of_contents"),
        gpt_params={
            "max_interactions": 10,
            "max_function_iterations": 10
        },
        context="""
The user will give you a table of contents of a book.
Your task is to transform the table of contents into a list of jsons of the following form: 
[
    {
        name: 'Chapter 1 name', 
        page: 1,
        sub: [
            {
                name: 'Subchapter 1 name', 
                page: 2,
                sub: [
                    {name: 'Subsubchapter 1 name', page: 3},
                    {name: 'Subsubchapter 2 name', page: 4},
                ]
            },
            {name: 'Subchapter 2 name', page: 5},
        ]
    },
    {name: 'Chapter 2 name', page: 12},
    {name: 'Chapter 3 name', page: 15},
]

If there are not page numbers, no problem. Just return the json without page numbers.
Make it as nested as necessary. 
First level is the chapter. Second level is the subchapter. Third level is the subsubchapter and so on. 
""",    
        inputPromptFormatString=f"{toc}",
        model="gpt-4.1-2025-04-14",
        can_throw=False,
    )()

    write_cache_table_of_contents(book, toc_json)
    return toc_json


def enrich_table_of_contents_with_characters(book: str, toc: dict) -> list[dict]:
    """
    Enrich the table of contents with character number information.

    Output format: 
    [
        {
            name: "Chapter 1 name",
            page: 1,
            character: 123,
        },
        {
            name: "Chapter 1 name: subchapter 1 name",
            page: 12,
            character: 456,
        },
        {
            name: "Chapter 1 name: subchapter 1 name: subsubchapter 1 name",
            page: 12,
            character: 521,
        },
        {
            name: "Chapter 1 name: subchapter 1 name: subsubchapter 2 name",
            page: 12,
            character: 652,
        },
        {
            name: "Chapter 1 name: subchapter 2 name",
            page: 12,
            character: 712,
        },
        {
            name: "Chapter 2 name",
            page: 12,
            character: 766,
        },
        {
            name: "Chapter 3 name",
            page: 15,
            character: 789,
        },
    ]
    """
    if read_cache_enriched_table_of_contents(book) is not None:
        print("Enriched table of contents found in cache.")
        return read_cache_enriched_table_of_contents(book)
    else:
        print("Enriched table of contents not found in cache. Enriching it.")
    
    #flatten the toc
    toc_flat = []
    def flatten_toc(toc: dict, level: int = 0):
        for item in toc:
            name = item["name"]
            page = item.get("page", None)
            sub = item.get("sub", [])
            toc_flat.append({
                "name": f"{name}",
                "page": page,
                "level": level,
            })
            if len(sub) > 0: flatten_toc(sub, level + 1)

    flatten_toc(toc)
    
    enriched_toc = []
    cutoff = 0

    for i in range( len(toc_flat)-1): 

        name = toc_flat[i]["name"]
        page = toc_flat[i].get("page", None)
        level = toc_flat[i]["level"]

        next_book_part = book[cutoff:cutoff+ASSUME_LARGEST_SUBSUBCHAPTER_LENGTH]

        print("Next book part: ")
        print("====================================================================================================================================================================================================================================")
        print(next_book_part)
        print("====================================================================================================================================================================================================================================")

        print("Looking for the start of the chapter:")
        print(name)
        
        def validator_function(starting_string) -> Optional[str]:
            """
            Validate the function by checking if the toc is in the book.
            """
            if find_substring_with_tolerance(next_book_part, starting_string, tolerance=80)[0]: 
                return 
            else: 
                return "That string is not in the part of the book. Please try again."

        foo = Funktion(
            returnType=Parameter(type=str, name="starting_string"),
            gpt_params={
                "max_interactions": 10,
                "max_function_iterations": 10
            },
            context=f"""
The user will give you a part of a pdf of a book. The part is somewhere in the book. 
Your task is to find the a {''.join(["sub" for _ in range(level)])}chapter in the part of the book.
The {''.join(["sub" for _ in range(level)])}chapter is called '{name}'.

Please return the string with which the {''.join(["sub" for _ in range(level)])}chapter '{name}' starts. 
Including the name of the {''.join(["sub" for _ in range(level)])}chapter or the headline.

The string could be the headline + the first two sentences or so.
""",    
            inputPromptFormatString=f"{next_book_part}",
            model="gpt-4.1-2025-04-14",
            can_throw=True,
            returnValidator=validator_function,
        )

        starting_string = foo()

        char = find_substring_with_tolerance(next_book_part, starting_string, tolerance=80)[0]
        if char == -1:
            print(f"String not found in book: {starting_string}")
            Exception("String not found in book.")
        
        #Char is wrong here, might be a bug in the return of find_substring_with_tolerance

        cutoff += char 

        toc_flat[i]["character"] = cutoff

        print("Chapter starts with")
        print(starting_string)

        print("Chapter starts at character")
        print(cutoff)

        print("Chapter start: ")
        print(book[cutoff:cutoff+500])

        if i == 3: return 

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




if __name__ == "__main__":
    # Example usage
    book = "test/Lodovico_Satana.pdf"  # Replace with your PDF file path
    from pdf_reader import extract_text
    txt = extract_text(book)

    list_of_files = transform(txt, max_length_book_as_single_file=10000)
    print(list_of_files)


