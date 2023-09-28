from pathlib import Path

from pytube import YouTube
from whisper import load_audio


class Transcribe:
    def __init__(self, model_provider, temp_dir) -> None:
        self._model_provider = model_provider
        self.temp_dir = Path(temp_dir)

    def transcribe_file(self, file: str | Path, language=None):
        try:
            with self._model_provider as model:
                audio = load_audio(str(file))
                result = model.transcribe(
                    audio=audio,
                    language=language,
                )
            return result

        finally:
            self.remove_files([file])

    def transcribe_multiple(self, file_list: list[str | Path], language=None):
        results = []
        try:
            with self._model_provider as model:
                for file_path in file_list:
                    audio = load_audio(str(file_path))
                    result = model.transcribe(
                        audio=audio,
                        language=language,
                    )
                    results.append(result)

        finally:
            self.remove_files(file_list)

    def is_path(self, string):
        string = Path(string)
        if string.exists():
            return True
        else:
            return False

    @staticmethod
    def remove_files(files_list):
        for file_path in files_list:
            file_path = Path(file_path)
            file_path.unlink(True)


class TranscribeYoutube(Transcribe):
    def __init__(self, model_provider, temp_dir) -> None:
        super().__init__(model_provider, temp_dir)

    def transcribe_youtube(self, youtubelink: str, language=None):
        audio_file_path = self.get_audio(youtubelink)
        self.transcribe_file(audio_file_path, language=language)

    def get_title(self, link):
        yt = YouTube(link)
        return yt.title

    def get_audio(self, link):
        yt = YouTube(link)
        return yt.streams.get_audio_only().download(
            filename=str(self.temp_dir))
