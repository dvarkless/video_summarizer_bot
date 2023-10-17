from pathlib import Path

from src.compose.composers import Composer
from src.compose.markdown import Markdown
from src.config import Config
from src.process.agent import MapReduceSplitter
from src.process.file_process import Transcribe, TranscribeYoutube
from src.process.model import ConfigureModel
from src.process.prompt import get_prompt
from src.bot.exceptions import LLMError, ConfigAccessError, ComposerError, LinkError


def run_summary(
        title: str,
        text_path: str | Path,
        model_name: str,
        doc_format: str,
        text_structure: str,
        answer_language: str = 'auto',
        temp_name: str = 'temp',
        yt_link: str | None = None,
):
    # Constants
    document_names = {
        'markdown': Markdown,
    }
    # Configs
    models_config = Config('./configs/models_text.yaml')
    try:
        my_config = models_config[model_name]
        max_tokens = my_config['available_context']
        model_provider = ConfigureModel(model_name, models_config)
    except KeyError as ex:
        raise ConfigAccessError(f"Unknown config name: '{model_name}'") from ex
    except Exception as ex:
        raise LLMError('Error in model creation') from ex

    embeddings_config = Config("./configs/embeddings.yaml")
    try:
        embeddings_provider = ConfigureModel(model_name, embeddings_config)
    except KeyError as ex:
        raise ConfigAccessError(f"Unknown config name: '{model_name}'") from ex
    except Exception as ex:
        raise LLMError('Error in model creation') from ex

    try:
        summary_prompt_config = Config("./configs/prompts.yaml")[text_structure]
    except KeyError as ex:
        raise ConfigAccessError(f"Unknown config name: '{text_structure}'") from ex

    if answer_language == 'auto':
        language_prompt = ", write your answer in the same language used in the text"
    else:
        language_prompt = f", write your answer in {answer_language}"
    model_template = {
        'system': my_config["system_template"],
        'instruction': my_config["instruction_template"],
        'response': my_config["response_template"],
        'misc': language_prompt,
    }
    # Prompts
    premap_prompt = get_prompt(
        summary_prompt_config["premap"], model_template)
    map_prompt = get_prompt(
        summary_prompt_config["map"], model_template)
    postmap_prompt = get_prompt(
        summary_prompt_config["postmap"], model_template)
    reduce_prompt = get_prompt(
        summary_prompt_config["reduce"], model_template)
    # Handle different return types
    if premap_prompt is None:
        premap_prompts = None
    elif isinstance(premap_prompt, str):
        premap_prompts = {summary_prompt_config["premap_name"]: premap_prompt}
    else:
        premap_prompts = {name: prompt
                          for name, prompt in zip(
                              summary_prompt_config['premap_name'], premap_prompt)}

    if postmap_prompt is None:
        postmap_prompts = None
    elif isinstance(postmap_prompt, str) or postmap_prompt is None:
        postmap_prompts = {
            summary_prompt_config["postmap_name"]: postmap_prompt}
    else:
        postmap_prompts = {name: prompt
                           for name, prompt in zip(
                               summary_prompt_config['premap_name'], postmap_prompt)}
    # Text summary
    try:
        summary = MapReduceSplitter(model_provider,
                                    embeddings_provider,
                                    map_prompt,
                                    reduce_prompt,
                                    premap_prompts=premap_prompts,
                                    postmap_prompts=postmap_prompts,
                                    window_len=my_config['window_len'],
                                    window_overlap=my_config['window_overlap'],
                                    max_tokens=max_tokens,
                                    )
        output_dict = summary.run(text_path, doc_name=title)
    except Exception as ex:
        raise LLMError('Error in MapReduceSplitter') from ex
    if yt_link is not None:
        output_dict['link'] = yt_link
    # Compose and save summary document
    document = document_names[doc_format]('./temp', temp_name)
    try:
        composer = Composer(document)
        if text_structure == 'facts_youtube':
            composer.facts_youtube(output_dict)
        elif text_structure == 'facts_video':
            composer.facts_video(output_dict)

        elif text_structure == 'speech_youtube':
            composer.speech_youtube(output_dict)
        elif text_structure == 'speech_video':
            composer.speech_video(output_dict)

        elif text_structure == 'dry_youtube':
            composer.dry_youtube(output_dict)
        elif text_structure == 'dry_video':
            composer.dry_video(output_dict)
    except Exception as ex:
        raise ComposerError('Error while composing document') from ex


def get_text_youtube(link, model_name, temp_name='temp'):
    models_config = Config('./configs/models_audio.yaml')
    try:
        model_provider = ConfigureModel(model_name, models_config)
    except KeyError as ex:
        raise ConfigAccessError(f"Unknown config name: '{model_name}'") from ex
    except Exception as ex:
        raise LLMError('Error in model creation') from ex
    transcriber = TranscribeYoutube(model_provider, f"./temp/{temp_name}.mp4")
    transcriber.load_link(link)
    text = transcriber.transcribe_youtube()
    title = transcriber.yt.title or 'title'
    return text, title


def get_text_local(file_path, model_name, temp_name='temp'):
    models_config = Config('./configs/models_audio.yaml')
    try:
        model_provider = ConfigureModel(model_name, models_config)
    except KeyError as ex:
        raise ConfigAccessError(f"Unknown config name: '{model_name}'") from ex
    except Exception as ex:
        raise LLMError('Error in model creation') from ex
    transcriber = Transcribe(model_provider, f"./temp/{temp_name}.mp4")
    text = transcriber.transcribe_file(file_path)
    return text
