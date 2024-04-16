import whisper


class Whisperer:

    def __init__(self):
        self.model = whisper.load_model("base")

    def transcribe(self, path: str):
        result = self.model.transcribe(path, language="french")
        return result["text"]
