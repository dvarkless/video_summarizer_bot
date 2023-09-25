# Model
# Embedding Support
from langchain.embeddings import LlamaCppEmbeddings, OpenAIEmbeddings
from langchain.llms import LlamaCpp, OpenAI


class ConfigureModel:
    model_names = {
            'LlamaCpp': LlamaCpp,
            'OpenAI': OpenAI,
            'OpenAIEmbeddings': OpenAIEmbeddings,
            'LlamaCppEmbeddings': LlamaCppEmbeddings,
            }

    local_models = [
            'LlamaCpp'
            ]

    def __init__(self, model_type, model_name, config) -> None:
        self._model_type = model_type
        self._model_name = model_name
        self._config = config

    def _configure_model(self):
        model_class_name = self._config[self._model_name]['class_name']
        model_kwargs = self._config[self._model_name]['model_params']
        model_class = self.model_names[model_class_name]
        return model_class(**model_kwargs)

    def get_model(self):
        self.model = self._configure_model()
        return self.model

    def get_model_type(self):
        return self._model_type
