def student_card(s):
    return (
        f"👤 {s['name']}\n"
        f"🎓 Класс: {s['class']}\n"
        f"📘 Предмет: {s['subjects'][0]}\n"
        f"🗓 Урок: {s['lesson_datetime']}"
    )
