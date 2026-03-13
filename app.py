from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import json
import os
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = "daily_routine_secret"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TASKS_PATH = os.path.join(BASE_DIR, "tasks.json")
DB_PATH = os.path.join(BASE_DIR, "routine.db")


# ---------------- DATABASE ---------------- #

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS routine (
        date TEXT PRIMARY KEY,
        data TEXT
    )
    """)

    conn.commit()
    conn.close()


# ---------------- TASKS ---------------- #

def load_tasks():
    if os.path.exists(TASKS_PATH):
        with open(TASKS_PATH, "r") as f:
            return json.load(f)
    return []


def save_tasks(tasks):
    with open(TASKS_PATH, "w") as f:
        json.dump(tasks, f, indent=2)


# ---------------- ROUTINE DATA ---------------- #

def get_today_status():
    today = date.today().isoformat()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT data FROM routine WHERE date=?", (today,))
    row = cursor.fetchone()

    conn.close()

    if row:
        return json.loads(row[0])
    return {}


def update_today_progress(form_data):
    today = date.today().isoformat()
    tasks = load_tasks()

    status = {}

    for task in tasks:
        status[task] = "✔" if form_data.get(task) else ""

    # auto mark X at 11:59
    now = datetime.now()
    if now.hour == 23 and now.minute == 59:
        for task in tasks:
            if status[task] == "":
                status[task] = "X"

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR REPLACE INTO routine (date, data) VALUES (?, ?)",
        (today, json.dumps(status, ensure_ascii=False))
    )

    conn.commit()
    conn.close()


# ---------------- SPECIAL DAY ---------------- #

def is_curd_rice_day():
    today = date.today().strftime("%A")
    return today in ["Tuesday", "Thursday", "Saturday"]


# ---------------- ROUTES ---------------- #

@app.route("/", methods=["GET", "POST"])
def index():

    tasks = load_tasks()

    if is_curd_rice_day():
        tasks = tasks + ["Curd Rice"]

    task_status = get_today_status()

    if request.method == "POST":
        update_today_progress(request.form)
        flash("Progress updated successfully!", "success")
        return redirect(url_for("index"))

    return render_template(
        "index.html",
        tasks=tasks,
        task_status=task_status
    )


@app.route("/manage", methods=["GET", "POST"])
def manage():

    tasks = load_tasks()

    if request.method == "POST":

        # ADD TASK
        if request.form.get("add"):
            new_task = request.form.get("new_task", "").strip()

            if new_task and new_task not in tasks:
                tasks.append(new_task)
                save_tasks(tasks)
                flash(f'Added "{new_task}"', "success")

            return redirect(url_for("manage"))

        # DELETE TASK
        delete_task = request.form.get("delete_task")

        if delete_task in tasks:
            tasks.remove(delete_task)
            save_tasks(tasks)
            flash(f'Deleted "{delete_task}"', "success")

        return redirect(url_for("manage"))

    return render_template("manage.html", tasks=tasks)


# ---------------- START SERVER ---------------- #

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)