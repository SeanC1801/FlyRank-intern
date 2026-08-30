import os

import psycopg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]


def get_connection():
    return psycopg.connect(DATABASE_URL)


def init_db():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    done BOOLEAN NOT NULL DEFAULT FALSE
                )
                """
            )
            cur.execute("SELECT COUNT(*) FROM tasks")
            (count,) = cur.fetchone()
            if count == 0:
                cur.execute(
                    "INSERT INTO tasks (title, done) VALUES "
                    "('Buy groceries', FALSE), "
                    "('Write report', FALSE), "
                    "('Walk the dog', TRUE)"
                )
        conn.commit()


def get_all_tasks():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, done FROM tasks ORDER BY id")
            rows = cur.fetchall()
    return [{"id": r[0], "title": r[1], "done": r[2]} for r in rows]


def get_task_by_id(task_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, title, done FROM tasks WHERE id = %s", (task_id,)
            )
            row = cur.fetchone()
    if row is None:
        return None
    return {"id": row[0], "title": row[1], "done": row[2]}
