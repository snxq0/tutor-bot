import asyncio
from datetime import datetime

from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart

from config import BOT_TOKEN
from storage import load_students, update_student, delete_student, add_lesson
from keyboards import (
    main_menu,
    students_menu,
    student_actions,
    confirm_delete
)
from messages import student_card

bot = Bot(BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

state = {}  # user_id -> {action, student}

# ---------- START ----------
@router.message(CommandStart())
async def start(message: Message):
    await message.answer("Панель репетитора 👇", reply_markup=main_menu())

# ---------- BACK ----------
@router.callback_query(F.data == "back")
async def back(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text("Панель репетитора 👇", reply_markup=main_menu())

# ---------- STUDENTS ----------
@router.callback_query(F.data == "students")
async def students(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text("👨‍🎓 Ученики", reply_markup=students_menu())

@router.callback_query(F.data == "students_list")
async def students_list(call: CallbackQuery):
    await call.answer()
    data = load_students()

    kb = InlineKeyboardMarkup(inline_keyboard=[])

    for sid, s in data.items():
        kb.inline_keyboard.append([
            InlineKeyboardButton(
                text=s["name"],
                callback_data=f"student:{sid}"
            )
        ])

    # ❗ ВОТ ТУТ БЫЛ БАГ — ИСПРАВЛЕНО
    kb.inline_keyboard.append([
        InlineKeyboardButton(
            text="⬅ Назад",
            callback_data="students"
        )
    ])

    await call.message.edit_text("Выбери ученика:", reply_markup=kb)

@router.callback_query(F.data.startswith("student:"))
async def student_view(call: CallbackQuery):
    await call.answer()
    sid = call.data.split(":")[1]
    s = load_students()[sid]

    await call.message.edit_text(
        student_card(s),
        reply_markup=student_actions(sid)
    )

# ---------- EDIT CLASS ----------
@router.callback_query(F.data.startswith("edit_class:"))
async def edit_class(call: CallbackQuery):
    await call.answer()
    sid = call.data.split(":")[1]
    state[call.from_user.id] = {"action": "class", "student": sid}
    await call.message.edit_text("Введи новый класс:")

# ---------- EDIT DATETIME ----------
@router.callback_query(F.data.startswith("edit_datetime:"))
async def edit_datetime(call: CallbackQuery):
    await call.answer()
    sid = call.data.split(":")[1]
    state[call.from_user.id] = {"action": "datetime", "student": sid}
    await call.message.edit_text(
        "Введи дату и время:\n"
        "YYYY-MM-DD HH:MM\n"
        "Пример: 2026-02-20 17:30"
    )

# ---------- ADD LESSON ----------
@router.callback_query(F.data.startswith("add_lesson:"))
async def lesson_topic(call: CallbackQuery):
    await call.answer()
    sid = call.data.split(":")[1]
    state[call.from_user.id] = {"action": "lesson", "student": sid}
    await call.message.edit_text("Введи тему урока:")

# ---------- DELETE ----------
@router.callback_query(F.data.startswith("delete_student:"))
async def delete_student_confirm(call: CallbackQuery):
    await call.answer()
    sid = call.data.split(":")[1]
    await call.message.edit_text(
        "⚠ Ты уверен, что хочешь удалить ученика?",
        reply_markup=confirm_delete(sid)
    )

@router.callback_query(F.data.startswith("confirm_delete:"))
async def delete_student_final(call: CallbackQuery):
    await call.answer()
    sid = call.data.split(":")[1]
    delete_student(sid)
    await call.message.edit_text("🗑 Ученик удалён", reply_markup=main_menu())

# ---------- TEXT INPUT ----------
@router.message(F.from_user.id.in_(state))
async def handle_input(message: Message):
    data = state.pop(message.from_user.id)
    sid = data["student"]

    if data["action"] == "class":
        update_student(sid, "class", message.text)
        await message.answer("Класс обновлён ✅", reply_markup=main_menu())

    elif data["action"] == "datetime":
        try:
            dt = datetime.strptime(message.text, "%Y-%m-%d %H:%M")
        except ValueError:
            await message.answer("❌ Неверный формат. Попробуй ещё раз.")
            state[message.from_user.id] = data
            return

        update_student(sid, "lesson_datetime", dt.strftime("%Y-%m-%d %H:%M"))
        await message.answer("Дата и время обновлены ✅", reply_markup=main_menu())

    elif data["action"] == "lesson":
        s = load_students()[sid]
        add_lesson(sid, s["subjects"][0], message.text)
        await message.answer("Урок добавлен ✅", reply_markup=main_menu())

# ---------- MAIN ----------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
