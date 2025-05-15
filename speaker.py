import os 

def speak_file(path: str) -> None:
    """
    Takes a txt file which is a preprocessed chunk of a book and speaks it.
    If its cached it will be skipped.
    Stores the spoken text in a new file.
    Name of the file is the path of the original file but as mp3.
    Args:
        path (str): The path to the prepocessed chunk txt file.
    """
    base_name, extension = os.path.splitext(path)
    spoken_file = f"{base_name}.mp3"
    
    if os.path.exists(spoken_file):
        print(f"Spoken file already exists: {spoken_file}")
        return

    with open(path, 'r') as file:
        text = file.read()

    spoken_text = speak(text)

    #write the spoken text to a file #TODO
    with open(spoken_file, 'wb') as file:
        file.write(spoken_text)

    print(f"Spoken text written to: {spoken_file}")


def speak(text: str):
    return b"0x12" #TODO