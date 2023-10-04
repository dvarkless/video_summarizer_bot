from aiogram import F, Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile

from src.bot.bot_locale import BotReply
from src.bot.keyboard import keyboard
from src.bot.actions import run_summary, get_text_local, get_text_youtube

import re
import time

router = Router()
replies = BotReply()


@router.message(F.video)
async def video_handler(message: Message, bot: Bot) -> None:
    file_path = f'./tmp/{message.video[-1].file_id}.mp4'
    await bot.download(
            message.video[-1],
            destination=file_path
            )
    # DB access
    text, title = get_text_local(file_path)
    txt_path = f'./temp/{get_temp_name()}.txt'
    with open(txt_path, 'w') as f:
        f.writelines(text)
    # DB access
    temp_name = get_temp_name('audio')
    summary_path = f'./temp/{temp_name}.mp4'
    run_summary(txt_path, text_title=title)
    doc_file = FSInputFile(summary_path)
    caption = replies.answers(message.from_user.id, 'general')['document_caption']
    await message.answer_document(
        doc_file,
        caption
    )


@router.message(F.text)
async def link_handler(message: Message, bot: Bot) -> None:
    get_link_regex = re.compile(r'https://www.youtube.com/watch\S+')
    link = get_link_regex.findall(message.text)[0]

    # DB access
    text, title = get_text_youtube(link)
    txt_path = f'./temp/{get_temp_name()}.txt' 
    with open(txt_path, 'w') as f:
        f.writelines(text)
    # DB access
    temp_name = get_temp_name('audio')
    summary_path = f'./temp/{temp_name}.mp4'
    run_summary(txt_path, text_title=title)
    doc_file = FSInputFile(summary_path)
    caption = replies.answers(message.from_user.id, 'general')['document_caption']
    await message.answer_document(
        doc_file,
        caption
    )


def get_temp_name(prefix=''):
    curr_time = time.time()
    return time.strftime("temp-%B-%d-%H-%M-%S", curr_time)
