import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove

from src.bot.action_handlers import user_tasks
from src.bot.bot_locale import BotReply
from src.bot.keyboard import keyboard
from src.database import Database
from src.setup_handler import get_handler

router = Router()
replies = BotReply()
database = Database()

logger = logging.getLogger(__name__)
logger.addHandler(get_handler())


@router.message(CommandStart())
async def start_bot(message: Message) -> None:
    logger.info('Call: start_bot')
    user_lang_code = message.from_user.language_code
    user_id = message.from_user.id
    user_lang = None
    for key, vals in replies.replicas.items():
        if user_lang_code in vals["code"]:
            user_lang = key
    if user_lang is None:
        user_lang = "English"
        logger.warning(
            f'Cannot find users[{message.from_user.username}] language, setting {user_lang}')

    with database as db:
        db.update_settings(user_id, {"change_language": user_lang})

    await message.answer(
        replies.message(message.from_user.id, 'start'),
    )


@router.message(Command('help'))
async def help_handler(message: Message) -> None:
    logger.info('Call: help_handler')
    await message.answer(
        replies.message(message.from_user.id, 'help'),
    )


@router.message(Command('cancel'))
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """
    Allow user to cancel any action
    """
    logger.info('Call: cancel_handler')
    user_id = message.from_user.id

    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()

        await message.answer(
            replies.message(user_id, 'cancel'),
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    if user_id in user_tasks:
        task = user_tasks[user_id]
        task.cancel()

        text = replies.message(user_id, 'cancel')
        await message.answer(text)
        return

    text = replies.answers(user_id, 'errors')['nothing_to_cancel']
    await message.answer(text)


def get_handlers(command: str, state_obj: State):
    # Create command handler
    logger.info(f'Creating: command-handler-{command}')
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
    logger.info(f'Creating: answer-handler-{command}')
    assert command in replies
    try:
        replies_dict = replies.get_for_language(
            replies.default_language, command)
    except KeyError as ex:
        msg = f'Error in language name "{replies.default_language}"'
        logger.error(msg)
        raise KeyError(msg) from ex
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
            answer_value = replies.translate_button(
                message.from_user.id,
                command,
                message.text,
            )
            data = {command: answer_value}
            db.update_settings(message.from_user.id, data)
        out = replies.message(
            message.from_user.id, command) + '<b>' + message.text + '</b>'

        await state.clear()
        await message.answer(
            out,
            reply_markup=ReplyKeyboardRemove(),
            parse_mode='HTML'
        )

    logger.info(f'Creating: wrong-handler-{command}')

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
