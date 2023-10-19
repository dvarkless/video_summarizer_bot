import logging
from pathlib import Path

from src.bot.exceptions import (AudioModelError, ComposerError,
                                ConfigAccessError, LinkError, LLMError)
from src.compose.composers import Composer
from src.compose.markdown import Markdown
from src.config import Config
from src.process.agent import MapReduceSplitter
from src.process.file_process import Transcribe, TranscribeYoutube
from src.process.model import ConfigureModel
from src.process.prompt import get_prompt
from src.setup_handler import get_handler

logger = logging.getLogger(__name__)
logger.addHandler(get_handler())


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
    logger.info('Call: run_summary')
    # Constants
    document_names = {
        'markdown': Markdown,
    }
    # Configs

    logger.info('run_summary: setting up configs')
    models_config = Config('./configs/models_text.yaml')
    try:
        my_config = models_config[model_name]
        max_tokens = my_config['available_context']
        model_provider = ConfigureModel(model_name, models_config)
    except KeyError as ex:
        msg = f"Unknown config name: '{model_name}'"
        logger.error(msg)
        raise ConfigAccessError(msg) from ex
    except Exception as ex:
        msg = 'Error in model creation'
        logger.error(msg)
        raise LLMError(msg) from ex

    embeddings_config = Config("./configs/embeddings.yaml")
    try:
        embeddings_provider = ConfigureModel(model_name, embeddings_config)
    except KeyError as ex:
        msg = f"Unknown config name: '{model_name}'"
        logger.error(msg)
        raise ConfigAccessError(msg) from ex
    except Exception as ex:
        msg = 'Error in model creation'
        logger.error(msg)
        raise LLMError(msg) from ex

    try:
        summary_prompt_config = Config(
            "./configs/prompts.yaml")[text_structure]
    except KeyError as ex:
        msg = f"Unknown config name: '{text_structure}'"
        logger.error(msg)
        raise ConfigAccessError(msg) from ex

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
    logger.info('run_summary: setting up prompts')
    premap_prompts = get_prompt(
        summary_prompt_config["premap"],
        prompt_name=summary_prompt_config.get("premap_name", None),
        constant_dict=model_template
    )
    map_prompts = get_prompt(
        summary_prompt_config["map"],
        constant_dict=model_template
    )
    postmap_prompts = get_prompt(
        summary_prompt_config["postmap"],
        prompt_name=summary_prompt_config.get("postmap_name", None),
        constant_dict=model_template
    )
    reduce_prompts = get_prompt(
        summary_prompt_config["reduce"],
        constant_dict=model_template
    )
    map_prompt = list(map_prompts.values())[0]
    reduce_prompt = list(reduce_prompts.values())[0]

    # Text summary
    logger.info('run_summary: running MapReduceSplitter')
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
        msg = 'Error in MapReduceSplitter'
        logger.error(msg)
        raise LLMError(msg) from ex
    if yt_link is not None:
        output_dict['link'] = yt_link

    # Compose and save summary document
    logger.info('run_summary: composing document')
    document = document_names[doc_format]('./temp', temp_name)
    out_path = document.path
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
        msg = 'Error while composing document'
        logger.error(msg)
        raise ComposerError(msg) from ex

    return out_path


def get_text_youtube(link, model_name, temp_name='temp'):
    logger.info('Call: get_text_youtube')

    models_config = Config('./configs/models_audio.yaml')
    temp_path = f"./temp/{temp_name}.mp4"
    try:
        model_provider = ConfigureModel(model_name, models_config)
    except KeyError as ex:
        msg = f"Unknown config name: '{model_name}'"
        logger.error(msg)
        raise ConfigAccessError(msg) from ex
    except Exception as ex:
        msg = 'Error in model creation'
        logger.error(msg)
        raise LLMError(msg) from ex

    try:
        transcriber = TranscribeYoutube(model_provider, temp_path)
        transcriber.load_link(link)
    except Exception as ex:
        msg = "Could not load video from the provided yt link"
        logger.error(msg)
        raise LinkError(msg) from ex

    try:
        text = transcriber.transcribe_youtube()
    except Exception as ex:
        msg = 'Error while transcribing video from yt'
        logger.error(msg)
        raise AudioModelError(msg) from ex
    title = transcriber.yt.title.casefold() or 'title'

    Path(temp_path).unlink(missing_ok=True)
    return text, title


def get_text_local(file_path, model_name, temp_name='temp'):
    logger.info('Call: get_text_local')

    models_config = Config('./configs/models_audio.yaml')
    temp_path = f"./temp/{temp_name}.mp4"
    try:
        model_provider = ConfigureModel(model_name, models_config)
    except KeyError as ex:
        msg = f"Unknown config name: '{model_name}'"
        logger.error(msg)
        raise ConfigAccessError(msg) from ex
    except Exception as ex:
        msg = 'Error in model creation'
        logger.error(msg)
        raise LLMError(msg) from ex

    try:
        transcriber = Transcribe(model_provider, temp_path)
        text = transcriber.transcribe_file(file_path)
    except Exception as ex:
        msg = 'Error while transcribing video from local file'
        logger.error(msg)
        raise AudioModelError(msg) from ex

    Path(file_path).unlink(missing_ok=True)
    Path(temp_path).unlink(missing_ok=True)
    return text
