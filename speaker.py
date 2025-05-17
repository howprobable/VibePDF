import os 
from dotenv import load_dotenv

load_dotenv() 

from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def speak_file(path: str, cache: bool =True) -> None:
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
    
    if os.path.exists(spoken_file) and cache:
        print(f"Spoken file already exists: {spoken_file}")
        return

    with open(path, 'r', encoding="utf-8") as file:
        text = file.read()

    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="ash",
        input=text, 
        instructions="You are reading an audiobook. Read it in standard german. Please read it in a natural and very calming way. Mumble a bit.",
    ) as response:
        response.stream_to_file(spoken_file)

    print(f"Spoken text written to: {spoken_file}")


if __name__ == "__main__":
    # Example usage
    speak_file("test/audio_test.txt", cache=False)