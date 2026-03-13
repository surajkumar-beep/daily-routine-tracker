from flask import Flask, render_template, request, redirect, url_for, flash
import csv
import json
import os
from datetime import datetime, date
import pandas as pd

app = Flask(__name__)
app.secret_key = 'daily_routine_secret'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, 'routine.csv')
TASKS_PATH = os.path.join(BASE_DIR, 'tasks.json')

# Load tasks from JSON
def load_tasks():
    if os.path.exists(TASKS_PATH):
        with open(TASKS_PATH, 'r') as f:
            return json.load(f)
    return []

# Get or create CSV header
def ensure_csv_header():
    if not os.path.exists(CSV_PATH):
        tasks = load_tasks()
        header = ['date'] + tasks
        with open(CSV_PATH, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(header)

# Load CSV data as DataFrame for easy manipulation
def load_csv_data():
    ensure_csv_header()
    df = pd.read_csv(CSV_PATH)
    return df

# Save DataFrame to CSV
def save_csv_data(df):
    df.to_csv(CSV_PATH, index=False, encoding='utf-8-sig')

# Get today's row status
def get_today_status():
    today = date.today().isoformat()
    df = load_csv_data()
    
    if today in df['date'].values:
        row = df[df['date'] == today].iloc[0]
        status = dict(row)
        del status['date']
        return {k: v == '✔' for k, v in status.items()}
    
    return {}

# Update today's progress
def update_today_progress(form_data):
    today = date.today().isoformat()
    df = load_csv_data()
    tasks = load_tasks()
    
    status_row = {'date': today}
    for task in tasks:
        status_row[task] = '✔' if form_data.get(task) else ''
    
    # Check if today exists
    if today in df['date'].values:
        # Update existing row
        idx = df[df['date'] == today].index[0]
        df.iloc[idx] = pd.Series(status_row)
    else:
        # Append new row
        new_row = pd.DataFrame([status_row])
        df = pd.concat([df, new_row], ignore_index=True)
    
    # Auto-mark missed tasks at end of day (23:59)
    now = datetime.now()
    if now.hour == 23 and now.minute == 59:
        for task in tasks:
            if df.iloc[-1][task] == '':
                df.iloc[-1][task] = 'X'
    
    save_csv_data(df)

# Check if special day for Curd Rice
def is_curd_rice_day():
    today = date.today().strftime('%A')
    return today in ['Tuesday', 'Thursday', 'Saturday']

@app.route('/', methods=['GET', 'POST'])
def index():
    tasks = load_tasks()
    if is_curd_rice_day():
        tasks = tasks + ['Curd Rice']
    
    task_status = get_today_status()
    if request.method == 'POST':
        update_today_progress(request.form)
        flash('Progress updated successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('index.html', tasks=tasks, task_status=task_status)

@app.route('/manage', methods=['GET', 'POST'])
def manage():
    tasks = load_tasks()
    if request.method == 'POST':
        if request.form.get('add'):
            new_task = request.form.get('new_task', '').strip()
            if new_task and new_task not in tasks:
                tasks.append(new_task)
                with open(TASKS_PATH, 'w') as f:
                    json.dump(tasks, f, indent=2)
                flash(f'Added "{new_task}"', 'success')
            return redirect(url_for('manage'))
        delete_task = request.form.get('delete_task')
        if delete_task in tasks:
            tasks.remove(delete_task)
            with open(TASKS_PATH, 'w') as f:
                json.dump(tasks, f, indent=2)
            flash(f'Deleted "{delete_task}"', 'success')
        return redirect(url_for('manage'))
    return render_template('manage.html', tasks=tasks)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

