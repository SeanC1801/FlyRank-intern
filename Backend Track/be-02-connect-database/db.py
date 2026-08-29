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

