import time
from pathlib import Path
from typing import Tuple, Union

import numpy as np
import torch
import whisper
from langchain.embeddings import LlamaCppEmbeddings, OpenAIEmbeddings
from langchain.embeddings.spacy_embeddings import SpacyEmbeddings
from langchain.llms import LlamaCpp, OpenAI
from whisper.tokenizer import LANGUAGES


class WhisperInference:
    def __init__(
            self,
            model_name,
            model_dir,
            is_translate,
            beam_size=1,
            **whisper_params
    ):
        self.model_name = model_name
        self.model_path = Path(model_dir)
        self.available_models = whisper.available_models()
        self.available_langs = sorted(
            list(LANGUAGES.values()))
        self.beam_size = beam_size
        self.is_translate = is_translate
        self.model = whisper.load_model(
            name=self.model_name, download_root=str(self.model_path), **whisper_params)
        self.input_files = []

    def transcribe(self,
                   audio: Union[str, np.ndarray, torch.Tensor],
                   language=None,
                   **to_whisper_transcribe,
                   ):
        start_time = time.time()

        result = self.model.transcribe(audio=audio,
                                       beam_size=self.beam_size,
                                       task="translate" if self.is_translate else "transcribe",
                                       language=language,
                                       **to_whisper_transcribe,
                                       )["text"]
        self.elapsed_time = time.time() - start_time

        return result

    def __del__(self):
        del self.model


class ConfigureModel:
    model_names = {
        'LlamaCpp': LlamaCpp,
        'OpenAI': OpenAI,
        'OpenAIEmbeddings': OpenAIEmbeddings,
        'LlamaCppEmbeddings': LlamaCppEmbeddings,
        'WhisperLocal': WhisperInference,
        'SpacyEmbeddings': SpacyEmbeddings,
    }

    local_models = [
        'LlamaCpp'
    ]

    def __init__(self, model_name, config) -> None:
        self._model_name = model_name
        self._config = config

    def __enter__(self):
        return self.get_model()

    def __exit__(self, exc_type, exc_value, traceback):
        del self.model

    def _configure_model(self):
        model_class_name = self._config[self._model_name]['provider']
        model_kwargs = self._config[self._model_name]['model_params']
        model_class = self.model_names[model_class_name]
        return model_class(**model_kwargs)

    def get_model(self):
        self.model = self._configure_model()
        return self.model
