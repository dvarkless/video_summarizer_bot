import logging
import re
from datetime import datetime
from functools import partial
from pathlib import Path
from traceback import format_exception

from aiogram import Bot, F, Router
from aiogram.filters.exception import ExceptionTypeFilter
from aiogram.types import ErrorEvent, Message
from pydub import AudioSegment

from src.bot.actions import (get_text_local, get_text_youtube, run_summary,
                             worker)
from src.bot.bot_locale import BotReply
from src.bot.exceptions import (AudioModelError, ComposerError,
                                ConfigAccessError, LinkError, LLMError,
                                TooManyTasksError)
from src.config import Config
from src.database import Database, user_tasks
from src.setup_handler import get_handler

router = Router()
replies = BotReply()
database = Database()
defaults = Config('./configs/settings_defaults.yaml')
bot_settings = Config('./configs/bot_settings.yaml')


logger = logging.getLogger(__name__)
logger.addHandler(get_handler())


def get_temp_name(prefix=''):
    curr_d = datetime.now()
    curr_t = curr_d.strftime("temp-%B-%d-%H-%M-%S")
    if prefix:
        prefix = prefix + '-'
    return prefix + curr_t


@router.message(F.video)
async def video_handler(message: Message, bot: Bot) -> None:
    logger.info('Call: video_handler')

    user_id = message.from_user.id
    if await is_generating(message):
        return

    file_name = message.video.file_name
    if file_name is None:
        msg = 'Could not find file name'
        logger.error(msg)
        raise ValueError(msg)
    file_path = Path(f'./temp') / file_name

    await bot.download(
        file=message.video.file_id,
        destination=file_path
    )

    await message.answer(
        replies.answers(message.from_user.id, 'general')[
            'got_video']
    )
    try:
        audio_path = f"./temp/{get_temp_name('audio')}.mp3"
        AudioSegment.from_file(str(file_path), file_path.suffix[1:]).export(
            audio_path, format='mp3')
        file_path.unlink(missing_ok=True)
    except Exception as ex:
        raise AudioModelError from ex

    # Preparing data
    with database as db:
        settings = db.get_settings(user_id)

    audio_model = bot_settings['audio_model']
    temp_name = get_temp_name('audio')
    text = get_text_local(audio_path, audio_model, temp_name)

    txt_path = f'./temp/{get_temp_name("txt")}.txt'
    with open(txt_path, 'w') as f:
        f.writelines(text)

    text_model = bot_settings['text_model']
    document_format = settings['document_format']
    document_language = settings['document_language']
    text_format = settings['text_format'] + '_video'

    temp_name = get_temp_name('file')
    summary_func = partial(
        run_summary,
        file_name,
        txt_path,
        text_model,
        document_format,
        text_format,
        answer_language=document_language,
        temp_name=temp_name,
    )
    wrapper = partial(message_wrapper, summary_func, message)
    await worker(message, wrapper)


@router.message(F.text)
async def link_handler(message: Message) -> None:
    logger.info('Call: link_handler')

    user_id = message.from_user.id
    if await is_generating(message):
        return
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

    # Preparing data
    with database as db:
        settings = db.get_settings(user_id)

    audio_model = bot_settings['audio_model']
    temp_name = get_temp_name('audio')
    text, title = get_text_youtube(link, audio_model, temp_name)

    txt_path = f'./temp/{get_temp_name("txt")}.txt'
    with open(txt_path, 'w') as f:
        f.writelines(text)

    text_model = bot_settings['text_model']
    document_format = settings['document_format']
    document_language = settings['document_language']
    text_format = settings['text_format'] + '_youtube'

    temp_name = get_temp_name('file')
    summary_func = partial(
        run_summary,
        title,
        txt_path,
        text_model,
        document_format,
        text_format,
        answer_language=document_language,
        temp_name=temp_name,
        yt_link=link,
    )
    wrapper = partial(message_wrapper, summary_func, message)
    await worker(message, wrapper)


def message_wrapper(foo, message: Message):
    out = foo()
    return out, message


async def is_generating(message: Message):
    user_id = message.from_user.id
    if user_tasks.get(user_id, None) is not None:
        text = replies.answers(user_id, 'general')['processing']
        await message.answer(text)
        return True
    else:
        return False


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


@router.error(ExceptionTypeFilter(TooManyTasksError), F.update.message.as_("message"))
async def audio_model_error(event: ErrorEvent, message: Message):
    id = message.from_user.id
    error_msg = replies.answers(id, 'errors')['too_many_tasks']
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
