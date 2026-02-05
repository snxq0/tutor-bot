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

def update_student(student_id, field, value):
    data = load_students()
    data[student_id][field] = value
    save_students(data)

def delete_student(student_id):
    data = load_students()
    if student_id in data:
        del data[student_id]
        save_students(data)

def add_lesson(student_id, subject, topic):
    data = load_students()
    data[student_id]["lessons_history"].append({
        "subject": subject,
        "topic": topic,
        "date": str(date.today())
    })
    save_students(data)
