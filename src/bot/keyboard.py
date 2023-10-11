from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def keyboard(butn_list: list, placeholder: str | None = None) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    buttons = sorted(butn_list)
    num_buttons = min(len(buttons), 4)
    for btn in buttons:
        kb.button(text=btn)
    kb.adjust(num_buttons)
    return kb.as_markup(resize_keyboard=True,
                        input_field_placeholder=placeholder)
