import os


def preprocess_file(path: str) -> str:
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
    
    if os.path.exists(preprocessed_file):
        print(f"Preprocessed file already exists: {preprocessed_file}")
        return preprocessed_file

    with open(path, 'r') as file:
        text = file.read()

    preprocessed_text = preprocess(text)

    with open(preprocessed_file, 'w') as file:
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
    return ' '.join(text.split()) #TODO 
