import os
from dotenv import load_dotenv  

load_dotenv()


from gptLang import Funktion, Parameter

def preprocess_file(path: str, cache: bool=True) -> str:
    """
    Takes a txt file which is a chunk of a book and preprocesses it.
    If its cached it will be read from the cache.
    Stores the preprocessed text in a new file.
    Name of the file is the path of the original file with _preprocessed added to it.
    Args:
        path (str): The path to the txt file.
    """
    base_name, extension = os.path.splitext(path)
    preprocessed_file = f"{base_name}_preprocessed{extension}"
    
    if os.path.exists(preprocessed_file) and cache:
        print(f"Preprocessed file already exists: {preprocessed_file}")
        return preprocessed_file

    with open(path, 'r', encoding="utf-8") as file:
        text = file.read()

    preprocessed_text = preprocess(text)

    with open(preprocessed_file, 'w', encoding="utf-8") as file:
        file.write(preprocessed_text)

    print(f"Preprocessed text written to: {preprocessed_file}")
    return preprocessed_file
    

def preprocess(text: str) -> str: 
    """
    Preprocess the text by removing unwanted characters and formatting.
    This function is a placeholder and should be implemented based on specific requirements.
    
    Args:
        text (str): The text to preprocess.
    
    Returns:
        str: The preprocessed text.
    """

    foo = Funktion(
        inputType=Parameter(type=str, name="text"),
        returnType=Parameter(type=str, name="revised_text"),
        gpt_params={
            "max_interactions": 10,
            "max_function_iterations": 10
        },
        context="""
You are an editor for an audiobook.
The user will give you a part of pdf of book. Might be a chapter or a part of a chapter. Or the intro or outro of a chapter. Or even the first page of a book.
The pdf was extracted with a pdf reader. So it might contain some unwanted characters, unwanted line breaks, unwanted spaces, unwanted new lines, unwanted page numbers, unwanted page breaks, unwanted characters, unwanted formatting.
Your task is to remove all unwanted characters and formatting and information that is not relevant for the audiobook.
Your returned text should be a clean and readable version of the original text. 
The reader should not notice that it was a pdf. The reader will record your output directly without proofreading it and it will be used for an audiobook without any further editing.
So please make sure that the text is clean and readable.
""",    
        inputPromptFormatString="{text}",
        model="gpt-4o-2024-05-13",
        can_throw=False,
    )


    output = foo(text=text)

    return output


if __name__ == "__main__":
    # Example usage
    preprocess_file("test/preprocessor_test.txt", cache=False)
