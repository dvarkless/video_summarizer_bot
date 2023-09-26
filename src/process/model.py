# Model
# Embedding Support
import re
import time
from pathlib import Path
from typing import Tuple, Union

import numpy as np
import torch
import whisper
from pytube import YouTube

from langchain.embeddings import LlamaCppEmbeddings, OpenAIEmbeddings
from langchain.llms import LlamaCpp, OpenAI


class WhisperInference:
    def __init__(self, model_name, model_path, file_path, is_translate, audio_extention='.mp4'):
        self.model_name = model_name
        self.model_path = Path(model_path)
        self.file_path = Path(file_path)
        self.available_models = whisper.available_models()
        self.available_langs = sorted(
            list(whisper.tokenizer.LANGUAGES.values()))
        self.default_beam_size = 1
        self.is_translate = is_translate
        self.model = whisper.load_model(
            name=self.model_name, download_root=self.model_path)
        self.input_files = []

    def get_title(self, link):
        yt = YouTube(link)
        return yt.title

    def get_audio(self, link):
        yt = YouTube(link)
        return yt.streams.get_audio_only().download(
            filename=str(self.file_path))

    def transcribe_file(self, file: str | Path):
        try:
            audio = whisper.load_audio(str(file))
            result = self.transcribe(audio=audio,
                                     )
            return result

        finally:
            self.remove_files([file])

    def transcribe_youtube(self, youtubelink: str):
        audio_file_path = self.get_audio(youtubelink)
        self.transcribe_file(audio_file_path)

    def transcribe(self,
                   audio: Union[str, np.ndarray, torch.Tensor],
                   ):
        start_time = time.time()

        result = self.model.transcribe(audio=audio,
                                       verbose=False,
                                       beam_size=self.default_beam_size,
                                       task="translate" if self.is_translate else "transcribe",
                                       )["text"]
        self.elapsed_time = time.time() - start_time

        return result

    @staticmethod
    def format_time(elapsed_time: float) -> str:
        hours, rem = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(rem, 60)

        time_str = ""
        if hours:
            time_str += f"{hours} hours "
        if minutes:
            time_str += f"{minutes} minutes "
        seconds = round(seconds)
        time_str += f"{seconds} seconds"

        return time_str.strip()

    def __del__(self):
        del self.model

    @staticmethod
    def remove_files(files_list):
        for file_path in files_list:
            file_path = Path(file_path)
            file_path.unlink(True)


class ConfigureModel:
    model_names = {
        'LlamaCpp': LlamaCpp,
        'OpenAI': OpenAI,
        'OpenAIEmbeddings': OpenAIEmbeddings,
        'LlamaCppEmbeddings': LlamaCppEmbeddings,
        'WhisperLocal': WhisperInference,
    }

    local_models = [
        'LlamaCpp'
    ]

    def __init__(self, model_name, config) -> None:
        self._model_type = model_type
        self._model_name = model_name
        self._config = config

    def _configure_model(self):
        model_class_name = self._config[self._model_name]['provider']
        model_kwargs = self._config[self._model_name]['model_params']
        model_class = self.model_names[model_class_name]
        return model_class(**model_kwargs)

    def get_model(self):
        self.model = self._configure_model()
        return self.model

    def get_model_type(self):
        return self._model_type
