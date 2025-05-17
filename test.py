from preprocessor import preprocess_file
from speaker import speak_file

if __name__ == "__main__":
    file = preprocess_file("test/preprocessor_test.txt", cache=False)
    speak_file(file, cache=False)
