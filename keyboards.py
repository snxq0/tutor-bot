from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить урок", callback_data="add_lesson")],
        [InlineKeyboardButton(text="📋 Ученики", callback_data="list_students")]
    ])
