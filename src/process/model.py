import logging
import time
from pathlib import Path
from typing import Tuple, Union

import numpy as np
from faster_whisper import WhisperModel
from langchain.embeddings import LlamaCppEmbeddings, OpenAIEmbeddings
from langchain.embeddings.spacy_embeddings import SpacyEmbeddings
from langchain.llms import LlamaCpp, OpenAI

from src.setup_handler import get_handler

logger = logging.getLogger(__name__)
logger.addHandler(get_handler())


class WhisperInference:
    def __init__(
            self,
            model_name,
            model_dir,
            is_translate,
            beam_size=5,
            **whisper_params
    ):
        self.model_name = model_name
        self.model_path = Path(model_dir)
        self.beam_size = beam_size
        self.is_translate = is_translate
        self.model = WhisperModel(
            model_name, compute_type='float16', download_root=model_dir)
        self.input_files = []
        self.elapsed_time = 0

    def transcribe(self,
                   audio: Union[str, np.ndarray],
                   language=None,
                   **to_whisper_transcribe,
                   ):
        logger.info('Call: WhisperInference.transcribe')

        start_time = time.time()

        result = self.model.transcribe(audio=audio,
                                       beam_size=self.beam_size,
                                       task="translate" if self.is_translate else "transcribe",
                                       language=language,
                                       without_timestamps=True,
                                       **to_whisper_transcribe,
                                       )[0]
        res_texts = (r.text for r in result)
        result = '\n'.join(res_texts)
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
        logger.info(f'Configuring {model_class_name}')
        return model_class(**model_kwargs)

    def get_model(self):
        logger.info('Call: ConfigureModel.get_model')
        self.model = self._configure_model()
        return self.model
