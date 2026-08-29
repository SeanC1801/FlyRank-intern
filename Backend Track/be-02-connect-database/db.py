import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]


def get_connection():
    return psycopg.connect(DATABASE_URL)


def init_db():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            # 1. Create the tasks table if it does not exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    done BOOLEAN DEFAULT FALSE
                )
            ''')

            # 2. Check if the table is empty
            cursor.execute("SELECT COUNT(*) FROM tasks")
            row_count, = cursor.fetchone()

            # 3. Seed three example tasks ONLY if the table is empty
            if row_count == 0:
                starting_tasks = (
                    ("Learn FastAPI with Postgres", False),
                    ("Set up Stage 1", True),
                    ("Practice parameterized queries", False),
                )
                cursor.executemany(
                    "INSERT INTO tasks (title, done) VALUES (%s, %s)",
                    starting_tasks,
                )
                print("--- Successfully seeded 3 example tasks into Postgres! ---")

        conn.commit()
