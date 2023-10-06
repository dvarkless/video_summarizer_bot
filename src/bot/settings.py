from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove

from src.bot.bot_locale import BotReply
from src.bot.keyboard import keyboard

router = Router()
replies = BotReply()


@router.message(Command("language"))
async def language_handler(message: Message) -> None:
    await message.answer(
        replies.message(message.from_user.id, 'change_language'),
        reply_markup=keyboard(replies.answers(
            message.from_user.id, 'change_language'))
    )


@router.message(F.text.in_(replies.buttons('change_language')))
async def language_answer(message: Message):
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
    await message.answer(
        replies.answers(message.from_user.id, 'general')['success'],
        reply_markup=ReplyKeyboardRemove()
    )
