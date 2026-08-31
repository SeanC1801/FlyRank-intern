import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

def get_connection():
    return psycopg.connect(DATABASE_URL)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            done BOOLEAN DEFAULT FALSE
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM tasks")
    row_count = cursor.fetchone()[0]

    if row_count == 0:
        cursor.execute(
            "INSERT INTO tasks (title, done) VALUES (%s, %s)",
            ("Learn FastAPI with Postgres", False)
        )
        cursor.execute(
            "INSERT INTO tasks (title, done) VALUES (%s, %s)",
            ("Set up Stage 1", True)
        )
        cursor.execute(
            "INSERT INTO tasks (title, done) VALUES (%s, %s)",
            ("Practice parametrized queries", False)
        )

    conn.commit()
    conn.close()

# Query Functions
def get_all_tasks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_task_by_id(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = %s", (task_id,))
    row = cursor.fetchone()
    conn.close()
    return row

# Inserting a row
def create_task(title, done):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id, title, done",
        (title, done)
    )
    row = cursor.fetchone()
    conn.commit()
    conn.close()
    return row

# Updating a task
def update_task(task_id, title, done):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM tasks WHERE id = %s", (task_id,))
    if cursor.fetchone() is None:
        conn.close()
        return None
    cursor.execute(
        "UPDATE tasks SET title = %s, done = %s WHERE id = %s",
        (title, done, task_id)
    )
    conn.commit()
    conn.close()
    return (task_id, title, done)

# Deleting a task
def delete_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM tasks WHERE id = %s", (task_id,))
    if cursor.fetchone() is None:
        conn.close()
        return False
    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    conn.close()
    return True
    
# Health Check for Connection
def check_connection():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    cursor.fetchone()
    conn.close()
