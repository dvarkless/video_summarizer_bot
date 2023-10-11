from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
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


@router.message(Command('help'))
async def help_handler(message: Message) -> None:
    await message.answer(
        replies.message(message.from_user.id, 'help'),
    )


@router.message(Command('cancel'))
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()

    await message.answer(
        replies.message(message.from_user.id, 'cancel'),
        reply_markup=ReplyKeyboardRemove(),
    )


def get_handlers(command: str, state_obj: State):
    # Create command handler
    assert command in replies

    @router.message(Command(command))
    async def handler(message: Message, state: FSMContext) -> None:
        await message.answer(
            replies.message(message.from_user.id, command),
            reply_markup=keyboard(replies.buttons(
                user_id=message.from_user.id,
                scope=command,
            ))
        )

        await state.set_state(state_obj)

    # Create answer handler
    # Check if the configs have the necessary keys
    assert command in replies
    try:
        replies_dict = replies.get_for_language(
            replies.default_language, command)
    except KeyError:
        raise KeyError(f'Error in language name "{replies.default_language}"')
    assert 'message' in replies_dict
    assert 'description' in replies_dict
    assert 'button1' in replies_dict

    @router.message(
        state_obj,
        F.text.in_(replies.buttons(scope=command))
    )
    async def answer_handler(message: Message, state: FSMContext) -> None:
        assert message.text is not None
        assert message.from_user.id is not None

        with database as db:
            data = {command: message.text}
            db.update_settings(message.from_user.id, data)
        out = replies.message(
            message.from_user.id, command) + '<b>' + message.text + '</b>'

        await state.clear()
        await message.answer(
            out,
            reply_markup=ReplyKeyboardRemove(),
            parse_mode='HTML'
        )

    @router.message(
        state_obj,
    )
    async def wrong_answer_handler(message: Message, state: FSMContext) -> None:
        assert message.from_user.id is not None
        out = replies._get_position(
            message.from_user.id, 'errors')['unknown_setting']

        await state.clear()
        await message.answer(
            out,
            reply_markup=ReplyKeyboardRemove(),
        )

    return handler, answer_handler, wrong_answer_handler


class SettingStates(StatesGroup):
    change_language = State()
    document_language = State()
    document_format = State()
    text_format = State()


handlers = get_handlers('change_language', SettingStates.change_language)
bot_language_handler, bot_language_answer_handler, bot_language_wrong_handler = handlers

handlers = get_handlers('document_language', SettingStates.document_language)
doc_language_handler, doc_language_answer_handler, doc_language_wrong_handler = handlers

handlers = get_handlers('document_format', SettingStates.document_format)
doc_format_handler, doc_format_answer_handler, doc_format_wrong_handler = handlers

handlers = get_handlers('text_format', SettingStates.text_format)
text_style_handler, text_style_answer_handler, text_style_wrong_handler = handlers
