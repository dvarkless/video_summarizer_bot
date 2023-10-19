import logging
import re
import subprocess
from datetime import datetime
from pathlib import Path
from traceback import format_exception

import imageio_ffmpeg
from aiogram import Bot, F, Router
from aiogram.filters.exception import ExceptionTypeFilter
from aiogram.types import ErrorEvent, FSInputFile, Message

from src.bot.actions import get_text_local, get_text_youtube, run_summary
from src.bot.bot_locale import BotReply
from src.bot.exceptions import (AudioModelError, ComposerError,
                                ConfigAccessError, LinkError, LLMError)
from src.config import Config
from src.database import Database
from src.setup_handler import get_handler

router = Router()
replies = BotReply()
database = Database()
defaults = Config('./configs/defaults.yaml')

logger = logging.getLogger(__name__)
logger.addHandler(get_handler())


@router.message(F.video)
async def video_handler(message: Message, bot: Bot) -> None:
    logger.info('Call: video_handler')

    file_name = message.video.file_name
    if file_name is None:
        msg = 'Could not find file name'
        logger.error(msg)
        raise ValueError(msg)
    file_path = Path(f'./temp') / file_name

    user_id = message.from_user.id
    await bot.download(
        file=message.video.file_id,
        destination=file_path
    )

    await message.answer(
        replies.answers(message.from_user.id, 'general')[
            'got_video']
    )
    audio_path = f"./temp/{get_temp_name('audio')}.mp3"
    extract_audio(input_path=str(file_path), out_path=audio_path)
    file_path.unlink(missing_ok=True)

    summary_path = bot_run_summary(
        user_id, audio_path=audio_path, title=message.video.file_name)

    doc_file = FSInputFile(summary_path)
    caption = replies.answers(message.from_user.id, 'general')[
        'document_caption']
    await message.answer_document(
        doc_file,
        caption
    )


@router.message(F.text)
async def link_handler(message: Message) -> None:
    logger.info('Call: link_handler')

    user_id = message.from_user.id
    get_link_regex = re.compile(r'https://www.youtube.com/watch\S+')
    try:
        link = get_link_regex.findall(message.text)[0]
    except IndexError as ex:
        msg = "The provided text is not a link from youtube"
        logger.error(msg)
        raise LinkError(msg) from ex

    await message.answer(
        replies.answers(message.from_user.id, 'general')[
            'got_link']
    )

    summary_path = bot_run_summary(user_id, yt_link=link, context=message)

    doc_file = FSInputFile(summary_path)
    caption = replies.answers(message.from_user.id, 'general')[
        'document_caption']
    await message.answer_document(
        doc_file,
        caption
    )


def bot_run_summary(user_id, audio_path=None,
                    yt_link=None, title='Title',
                    context: Message | None = None
                    ) -> Path:
    logger.info('Call: bot_run_summary')

    if audio_path is not None:
        run_mode = 'video'
    elif yt_link is not None:
        run_mode = 'youtube'
    else:
        msg = 'Video path and yt link are not provided'
        logger.error(msg)
        raise ValueError(msg)
    with database as db:
        settings = db.get_settings(user_id)

    audio_model = settings.get('audio_model', defaults['audio_model'])
    temp_name = get_temp_name('audio')
    if run_mode == 'video':
        text = get_text_local(audio_path, audio_model, temp_name)
    elif run_mode == 'youtube':
        text, title = get_text_youtube(
            yt_link, audio_model, temp_name=temp_name)
    else:
        msg = 'Video path and yt link are not provided'
        logger.error(msg)
        raise ValueError(msg)

    txt_path = f'./temp/{get_temp_name("txt")}.txt'
    with open(txt_path, 'w') as f:
        f.writelines(text)

    text_model = settings.get('text_model', defaults['text_model'])
    document_format = settings.get(
        'document_format', defaults['document_format'])
    document_language = settings.get(
        'document_language', defaults['document_language'])
    text_format = settings.get('text_format', defaults['text_format'])
    text_format = f"{text_format}_{run_mode}"

    temp_name = get_temp_name('file')
    summary_path = run_summary(
        title,
        txt_path,
        text_model,
        document_format,
        text_format,
        answer_language=document_language,
        temp_name=temp_name,
        yt_link=yt_link,
    )

    Path(txt_path).unlink(missing_ok=True)
    return summary_path


def extract_audio(input_path, out_path):
    logger.info('Call: extract audio')
    FFMPEG_BINARY = imageio_ffmpeg.get_ffmpeg_exe()

    command = [FFMPEG_BINARY,
               '-i', input_path,
               '-ss', '00:00:00',
               '-f', 'mp3',
               '-y', out_path]
    result = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        err_msg = result.stderr.decode().strip().split("\n")[-1]
        msg = f"Cannot extract audio, reason: {err_msg}"
        logger.error(msg)
        raise AudioModelError(msg)


def get_temp_name(prefix=''):
    curr_d = datetime.now()
    curr_t = curr_d.strftime("temp-%B-%d-%H-%M-%S")
    if prefix:
        prefix = prefix + '-'
    return prefix + curr_t


@router.error(ExceptionTypeFilter(LinkError), F.update.message.as_("message"))
async def link_not_found(event: ErrorEvent, message: Message):
    id = message.from_user.id
    error_msg = replies.answers(id, 'errors')['bad_link']
    await error_handler(event, message, error_msg)


@router.error(ExceptionTypeFilter(LLMError), F.update.message.as_("message"))
async def llm_error(event: ErrorEvent, message: Message):
    id = message.from_user.id
    error_msg = replies.answers(id, 'errors')['llm']
    await error_handler(event, message, error_msg)


@router.error(ExceptionTypeFilter(ConfigAccessError), F.update.message.as_("message"))
async def config_access_error(event: ErrorEvent, message: Message):
    id = message.from_user.id
    error_msg = replies.answers(id, 'errors')['config_access']
    await error_handler(event, message, error_msg)


@router.error(ExceptionTypeFilter(ComposerError), F.update.message.as_("message"))
async def composer_error(event: ErrorEvent, message: Message):
    id = message.from_user.id
    error_msg = replies.answers(id, 'errors')['composer']
    await error_handler(event, message, error_msg)


@router.error(ExceptionTypeFilter(AudioModelError), F.update.message.as_("message"))
async def audio_model_error(event: ErrorEvent, message: Message):
    id = message.from_user.id
    error_msg = replies.answers(id, 'errors')['audio_model']
    await error_handler(event, message, error_msg)


@router.error(ExceptionTypeFilter(FileNotFoundError), F.update.message.as_("message"))
async def file_not_found(event: ErrorEvent, message: Message):
    id = message.from_user.id
    error_msg = replies.answers(id, 'errors')['file_not_found']
    await error_handler(event, message, error_msg)


@router.error(F.update.message.as_("message"))
async def critical_error(event: ErrorEvent, message: Message):
    id = message.from_user.id
    error_msg = replies.answers(id, 'errors')['critical']
    await error_handler(event, message, error_msg)


async def error_handler(event: ErrorEvent, message: Message, error_msg: str):
    logger.warning(f'Calling error handler with msg "{error_msg}"')
    id = message.from_user.id
    with database as db:
        user_data = db.get_telegram(id)

    exc_type = type(event.exception)
    exc_val = event.exception
    tb = event.exception.__traceback__
    tb_message = ''.join(format_exception(
        exc_type, exc_val, tb, limit=-10))
    traceback_str = f"\nTraceback:\n```python\n{tb_message}\n```"
    logger.error(traceback_str)

    if not user_data.get('is_admin', False):
        traceback_str = ''
    msg = error_msg + traceback_str
    logger.error(msg)
    await message.answer(msg, parse_mode='MarkdownV2')
