import asyncio
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import BOT_TOKEN
from keyboards import main_menu
from storage import load_students, add_lesson, save_students, reset_notifications
from messages import reminder

bot = Bot(BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

scheduler = AsyncIOScheduler()
user_state = {}  # user_id -> student_id

# ---------- START ----------
@router.message(CommandStart())
async def start(message: Message):
    await message.answer("Панель репетитора 👇", reply_markup=main_menu())

# ---------- LIST STUDENTS ----------
@router.callback_query(F.data == "list_students")
async def list_students(call: CallbackQuery):
    data = load_students()
    if not data:
        await call.message.answer("Учеников пока нет")
        return

    text = "📋 Ученики:\n\n"
    for s in data.values():
        text += f"• {s['name']} — {s['subjects'][0]} — {s['lesson_datetime']}\n"

    await call.message.answer(text)

# ---------- ADD LESSON ----------
@router.callback_query(F.data == "add_lesson")
async def choose_student(call: CallbackQuery):
    data = load_students()
    kb = InlineKeyboardMarkup(inline_keyboard=[])

    for student_id, s in data.items():
        kb.inline_keyboard.append([
            InlineKeyboardButton(
                text=s["name"],
                callback_data=f"lesson_student:{student_id}"
            )
        ])

    await call.message.answer("Выбери ученика:", reply_markup=kb)

@router.callback_query(F.data.startswith("lesson_student:"))
async def ask_topic(call: CallbackQuery):
    student_id = call.data.split(":")[1]
    user_state[call.from_user.id] = student_id
    await call.message.answer("Напиши тему урока:")

@router.message(F.from_user.id.in_(user_state))
async def save_lesson(message: Message):
    student_id = user_state.pop(message.from_user.id)
    data = load_students()
    subject = data[student_id]["subjects"][0]

    add_lesson(student_id, subject, message.text)
    await message.answer("Урок сохранён ✅", reply_markup=main_menu())

# ---------- AUTO NOTIFY ----------
async def check_lessons():
    data = load_students()
    now = datetime.now()

    for student_id, s in data.items():
        lesson_dt = datetime.strptime(
            s["lesson_datetime"],
            "%Y-%m-%d %H:%M"
        )

        if (
            not s["notified"]
            and lesson_dt > now
            and lesson_dt - now <= timedelta(minutes=s["notify_before"])
        ):
            await bot.send_message(
                student_id,
                reminder(
                    s["name"],
                    s["subjects"][0],
                    lesson_dt.strftime("%d.%m.%Y %H:%M")
                )
            )
            s["notified"] = True

    save_students(data)

# ---------- MAIN ----------
async def main():
    scheduler.add_job(check_lessons, "interval", minutes=1)
    scheduler.add_job(reset_notifications, "cron", hour=0, minute=0)
    scheduler.start()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
