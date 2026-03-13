from flask import Flask, render_template, request, redirect, url_for, flash
import csv
import json
import os
from datetime import datetime, date
import pandas as pd

app = Flask(__name__)
app.secret_key = 'daily_routine_secret'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TASKS_PATH = os.path.join(BASE_DIR, 'tasks.json')
CSV_PATH = os.path.join(BASE_DIR, 'routine.csv')

def load_tasks():
    if os.path.exists(TASKS_PATH):
        with open(TASKS_PATH, 'r') as f:
            return json.load(f)
    return []

def get_user_csv_path():
    return CSV_PATH

def ensure_csv_header(csv_path):
    if not os.path.exists(csv_path):
        tasks = load_tasks()
        header = ['date'] + tasks
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(header)

def load_csv_data(csv_path):
    ensure_csv_header(csv_path)
    df = pd.read_csv(csv_path, dtype=str)
    return df

def save_csv_data(df, csv_path):
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')

def get_today_status(csv_path):
    today = date.today().isoformat()
    df = load_csv_data(csv_path)
    
    if today in df['date'].values:
        row = df[df['date'] == today].iloc[0]
        status = dict(row)
        del status['date']
        return {k: bool(v == '✔') for k, v in status.items()}
    return {}

def update_today_progress(form_data, csv_path):
    today = date.today().isoformat()
    df = load_csv_data(csv_path)
    tasks = load_tasks()
    
    status_row = {'date': today}
    for task in tasks:
        status_row[task] = '✔' if form_data.get(task) else ''
    
    if today in df['date'].values:
        idx = df[df['date'] == today].index[0]
        df.iloc[idx] = pd.Series(status_row)
    else:
        new_row = pd.DataFrame([status_row])
        df = pd.concat([df, new_row], ignore_index=True)
    
    now = datetime.now()
    if now.hour == 23 and now.minute == 59:
        for task in tasks:
            if df.iloc[-1][task] == '':
                df.iloc[-1][task] = 'X'
    
    save_csv_data(df, csv_path)

def is_curd_rice_day():
    today = date.today().strftime('%A')
    return today in ['Tuesday', 'Thursday', 'Saturday']

@app.route('/', methods=['GET', 'POST'])
def index():
    csv_path = get_user_csv_path()
    tasks = load_tasks()
    if is_curd_rice_day():
        tasks = tasks + ['Curd Rice']
    
    task_status = get_today_status(csv_path)
    
    if request.method == 'POST':
        update_today_progress(request.form, csv_path)
        flash('Progress updated successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('index.html', tasks=tasks, task_status=task_status)

@app.route('/manage', methods=['GET', 'POST'])
def manage():
    tasks = load_tasks()
    
    if request.method == 'POST':
        if request.form.get('add'):
            new_task = request.form.get('new_task', '').strip()
            if new_task.strip() and new_task not in tasks:
                tasks.append(new_task.strip())
                # Update CSV header - add new column
                try:
                    df = pd.read_csv(CSV_PATH)
                    if new_task not in df.columns:
                        df[new_task] = ''
                        df.to_csv(CSV_PATH, index=False, encoding='utf-8-sig')
                except:
                    pass
                with open(TASKS_PATH, 'w') as f:
                    json.dump(tasks, f)
                flash(f'✅ Added "{new_task}"!', 'success')
                return redirect(url_for('manage'))
        
        if request.form.get('delete_task'):
            delete_task = request.form.get('delete_task')
            print(f"Delete attempt: '{delete_task}'")  # Debug
            tasks = load_tasks()  # Reload fresh list
            print(f"Current tasks: {tasks}")  # Debug
            if delete_task in tasks:
                tasks.remove(delete_task)
                print(f"Removed {delete_task}, remaining: {tasks}")  # Debug
                # Update CSV safely
                try:
                    df = pd.read_csv(CSV_PATH)
                    print(f"CSV cols before: {list(df.columns)}")
                    if delete_task in df.columns:
                        df = df.drop(columns=[delete_task])
                        df.to_csv(CSV_PATH, index=False, encoding='utf-8-sig')
                        print(f"Dropped '{delete_task}' from CSV")
                    else:
                        print(f"'{delete_task}' not in CSV columns")
                except Exception as e:
                    print(f"CSV error: {e}")
                with open(TASKS_PATH, 'w') as f:
                    json.dump(tasks, f, indent=2)
                flash(f'🗑️ Deleted "{delete_task}" OK!', 'success')
            else:
                print(f"Task '{delete_task}' not found in {tasks}")
                flash(f'❌ "{delete_task}" not found!', 'error')
            return redirect(url_for('manage'))
        
        return redirect(url_for('manage'))
    
    return render_template('manage.html', tasks=tasks)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

