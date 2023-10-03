from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def keyboard(butn_dict: dict, placeholder: str | None = None) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    butn_dict = butn_dict.copy()
    buttons = sorted(butn_dict.items(), key=lambda x: x[0])
    num_buttons = min(len(buttons), 4)
    for _, val in buttons:
        kb.button(text=val)
    kb.adjust(num_buttons)
    return kb.as_markup(resize_keyboard=True,
                        input_field_placeholder=placeholder)
