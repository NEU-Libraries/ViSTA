from abc import ABC, abstractmethod


class TranscriptionModel(ABC):
    """
    Interface for classes that handle transcribing text from the back of the image
    """
    def __init__(self, image_file):
        self.image_file = image_file
        self.token_data = None
        with open("../../transcription_prompt.txt", "r") as file:
            self.prompt = file.read()
        #self.model <- model should be instantiated in constructor


    @abstractmethod
    def generate_transcription(self):
        """
        Generates transcription from image at self.file_path
        Inputs:
            - None
        Outputs:
            - self.transcription is initialized as a Transcription object
            - self.tokens is initialized with the number of tokens used in the request
        """
        pass

    @abstractmethod
    def get_total_tokens(self):
        """
        Gets the number of tokens used from the latest transcription request
        Inputs:
            - None
        Outputs:
            - Returns self.tokens
            OR
            - Returns message indicating no transcription requests have been made yet
        """
        pass
