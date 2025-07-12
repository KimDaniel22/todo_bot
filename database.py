import sqlite3
from contextlib import contextmanager

DATABASE_NAME = 'tasks.db'

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                task_text TEXT NOT NULL,
                is_completed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

def add_task(user_id, task_text):
    with get_db_connection() as conn:
        conn.execute('INSERT INTO tasks (user_id, task_text) VALUES (?, ?)', (user_id, task_text))
        conn.commit()

def get_tasks(user_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, task_text, is_completed FROM tasks WHERE user_id = ? ORDER BY created_at', (user_id,))
        return cursor.fetchall()

def delete_task(task_id, user_id):
    with get_db_connection() as conn:
        conn.execute('DELETE FROM tasks WHERE id = ? AND user_id = ?', (task_id, user_id))
        conn.commit()

def toggle_task(task_id, user_id):
    with get_db_connection() as conn:
        conn.execute('''
            UPDATE tasks 
            SET is_completed = NOT is_completed 
            WHERE id = ? AND user_id = ?
        ''', (task_id, user_id))
        conn.commit()