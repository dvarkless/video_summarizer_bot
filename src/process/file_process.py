from pathlib import Path

from pytubefix import YouTube
from whisper import load_audio


class Transcribe:
    def __init__(self, model_provider, temp_dir) -> None:
        self._model_provider = model_provider
        self.temp_dir = Path(temp_dir)

    def transcribe_file(
            self,
            file: str | Path,
            language=None,
            **to_whisper_transcribe
    ) -> str:
        try:
            with self._model_provider as model:
                audio = load_audio(str(file))
                result = model.transcribe(
                    audio=audio,
                    language=language,
                    **to_whisper_transcribe,
                )
            return result

        finally:
            self.remove_files([file])

    def transcribe_multiple(
            self,
            file_list: list[str | Path],
            language=None,
            **to_whisper_transcribe
    ) -> list[str]:
        results = []
        try:
            with self._model_provider as model:
                for file_path in file_list:
                    audio = load_audio(str(file_path))
                    result = model.transcribe(
                        audio=audio,
                        language=language,
                        **to_whisper_transcribe,
                    )
                    results.append(result)
            return results

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
        self.yt = None
        super().__init__(model_provider, temp_dir)

    def load_link(self, youtubelink: str):
        self.yt = YouTube(youtubelink)

    def transcribe_youtube(
            self,
            language=None,
            **to_whisper_transcribe
    ) -> str:
        audio_file_path = self.get_audio()
        result = self.transcribe_file(
            file=audio_file_path, language=language, **to_whisper_transcribe)
        return result

    def get_title(self):
        if self.yt is not None:
            return self.yt.title
        else:
            raise AttributeError("Call self.load_link first")

    def get_audio(self):
        if self.yt is not None:
            return self.yt.streams.get_audio_only().download(
                filename=str(self.temp_dir))
        else:
            raise AttributeError("Call self.load_link first")
