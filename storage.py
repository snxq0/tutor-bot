import json
from datetime import date

FILE = "students.json"

def load_students():
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_students(data):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def add_lesson(student_id, subject, topic):
    data = load_students()
    data[student_id]["lessons_history"].append({
        "subject": subject,
        "topic": topic,
        "date": str(date.today())
    })
    save_students(data)

def reset_notifications():
    data = load_students()
    for s in data.values():
        s["notified"] = False
    save_students(data)
