from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def keyboard(butn_list: list, placeholder: str | None = None) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    buttons = sorted(butn_list)
    rows = min(len(buttons), 4)
    columns = len(buttons) % 4
    for btn in buttons:
        kb.button(text=btn)
    kb.adjust(columns, rows)
    return kb.as_markup(resize_keyboard=True,
                        input_field_placeholder=placeholder)
