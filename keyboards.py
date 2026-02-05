from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("👨‍🎓 Ученики", callback_data="students")]
    ])

def students_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("📋 Список учеников", callback_data="students_list")],
        [InlineKeyboardButton("⬅ Назад", callback_data="back")]
    ])

def student_actions(student_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("✏ Класс", callback_data=f"edit_class:{student_id}")],
        [InlineKeyboardButton("🗓 Дата и время", callback_data=f"edit_datetime:{student_id}")],
        [InlineKeyboardButton("➕ Добавить урок", callback_data=f"add_lesson:{student_id}")],
        [InlineKeyboardButton("🗑 Удалить ученика", callback_data=f"delete_student:{student_id}")],
        [InlineKeyboardButton("⬅ Назад", callback_data="students_list")]
    ])

def confirm_delete(student_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("❌ Нет", callback_data=f"student:{student_id}")],
        [InlineKeyboardButton("✅ Да, удалить", callback_data=f"confirm_delete:{student_id}")]
    ])
