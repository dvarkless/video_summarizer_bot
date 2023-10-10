from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, ReplyKeyboardRemove

from src.bot.bot_locale import BotReply
from src.bot.keyboard import keyboard
from src.database import Database

router = Router()
replies = BotReply()
database = Database()


@router.message(CommandStart())
async def start_bot(message: Message) -> None:
    user_lang_code = message.from_user.language_code
    user_id = message.from_user.id
    user_lang = None
    for key, vals in replies.replicas.items():
        if user_lang_code in vals["code"]:
            user_lang = key
    if user_lang is None:
        user_lang = "English"
    with database as db:
        db.update_settings(user_id, {"change_language": user_lang})
    await message.answer(
        replies.message(message.from_user.id, 'welcome'),
    )


@router.message(Command("language"))
async def language_handler(message: Message) -> None:
    await message.answer(
        replies.message(message.from_user.id, 'change_language'),
        reply_markup=keyboard(replies.answers(
            message.from_user.id, 'change_language'))
    )


@router.message(F.text.in_(replies.buttons('change_language')))
async def language_answer(message: Message):
    with database as db:
        data = {'change_language': message.text}
        db.update_settings(message.from_user.id, data)
    await message.answer(
        replies.answers(message.from_user.id, 'general')['success'],
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(Command("format"))
async def format_handler(message: Message) -> None:
    await message.answer(
        replies.message(message.from_user.id, 'document_format'),
        reply_markup=keyboard(replies.answers(
            message.from_user.id, 'document_format'))
    )


@router.message(F.text.in_(replies.buttons('document_format')))
async def format_answer(message: Message):
    with database as db:
        data = {'document_format': message.text}
        db.update_settings(message.from_user.id, data)
    await message.answer(
        replies.answers(message.from_user.id, 'general')['success'],
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(Command("structure"))
async def structure_handler(message: Message) -> None:
    await message.answer(
        replies.message(message.from_user.id, 'text_format'),
        reply_markup=keyboard(replies.answers(
            message.from_user.id, 'text_format'))
    )


@router.message(F.text.in_(replies.buttons('text_format')))
async def structure_answer(message: Message):
    with database as db:
        data = {'text_format': message.text}
        db.update_settings(message.from_user.id, data)
    await message.answer(
        replies.answers(message.from_user.id, 'general')['success'],
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(Command("doclang"))
async def doclang_handler(message: Message) -> None:
    await message.answer(
        replies.message(message.from_user.id, 'document_language'),
        reply_markup=keyboard(replies.answers(
            message.from_user.id, 'document_language'))
    )


@router.message(F.text.in_(replies.buttons('document_language')))
async def doclang_answer(message: Message):
    with database as db:
        data = {'document_language': message.text}
        db.update_settings(message.from_user.id, data)
    await message.answer(
        replies.answers(message.from_user.id, 'general')['success'],
        reply_markup=ReplyKeyboardRemove()
    )
