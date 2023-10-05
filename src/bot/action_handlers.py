import re
import time

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import FSInputFile, Message, ReplyKeyboardRemove

from src.bot.actions import get_text_local, get_text_youtube, run_summary
from src.bot.bot_locale import BotReply
from src.bot.keyboard import keyboard
from src.config import Config
from src.database import Database

router = Router()
replies = BotReply()
database = Database()
defaults = Config('./configs/defaults.yaml')


@router.message(F.video)
async def video_handler(message: Message, bot: Bot) -> None:
    file_path = f'./tmp/{message.video.file_id}.mp4'
    file_name = message.video.file_name
    user_id = message.from_user.id
    await bot.download(
        message.video,
        destination=file_path
    )

    summary_path = bot_run_summary(user_id, video_path=file_path, title=file_name)

    doc_file = FSInputFile(summary_path)
    caption = replies.answers(message.from_user.id, 'general')[
        'document_caption']
    await message.answer_document(
        doc_file,
        caption
    )


@router.message(F.text)
async def link_handler(message: Message, bot: Bot) -> None:
    user_id = message.from_user.id
    get_link_regex = re.compile(r'https://www.youtube.com/watch\S+')
    link = get_link_regex.findall(message.text)[0]

    summary_path = bot_run_summary(user_id, yt_link=link)
    doc_file = FSInputFile(summary_path)
    caption = replies.answers(message.from_user.id, 'general')[
        'document_caption']
    await message.answer_document(
        doc_file,
        caption
    )


def bot_run_summary(user_id, video_path=None, yt_link=None, title=None):
    if video_path is not None:
        run_mode = 'video'
    if video_path is not None:
        run_mode = 'youtube'
    else:
        raise ValueError('Video path and yt link are not provided')
    with database as db:
        settings = db.get_settings(user_id)

    audio_model = settings.get('audio_model', defaults['audio_model'])

    temp_name = get_temp_name('audio')
    if run_mode == 'video':
        text = get_text_local(video_path, audio_model, temp_name)
    elif run_mode == 'youtube':
        text, title = get_text_youtube(yt_link, audio_model, temp_name=temp_name)
    else:
        raise ValueError('Video path and yt link are not provided')

    txt_path = f'./temp/{get_temp_name()}.txt'
    with open(txt_path, 'w') as f:
        f.writelines(text)

    text_model = settings.get('text_model', defaults['text_model'])
    document_format = settings.get(
        'document_format', defaults['document_format'])
    document_language = settings.get(
        'document_language', defaults['document_language'])
    text_format = settings.get('text_format', defaults['text_format'])
    temp_name = get_temp_name('audio')
    summary_path = f'./temp/{temp_name}.mp4'
    summary_path = run_summary(txt_path, text_model, document_format,
                               text_format, answer_language=document_language)
    return summary_path


def get_temp_name(prefix=''):
    curr_time = time.struct_time({'tm_sec': time.time()})
    template_str = f"{prefix}-temp-%B-%d-%H-%M-%S"
    return time.strftime(template_str, curr_time)
