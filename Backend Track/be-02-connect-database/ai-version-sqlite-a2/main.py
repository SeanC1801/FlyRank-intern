import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: str
    done: int

def init_db():
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks
                 (id INTEGER PRIMARY KEY, title TEXT, done INTEGER)''')
    c.execute("SELECT COUNT(*) FROM tasks")
    if c.fetchone()[0] == 0:
        c.executemany("INSERT INTO tasks (title, done) VALUES (?, ?)",
                      [("Task 1", 0), ("Task 2", 0), ("Task 3", 0)])
    conn.commit()
    conn.close()

init_db()

def get_db():
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/tasks")
def get_tasks():
    conn = get_db()
    tasks = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    return [dict(t) for t in tasks]

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return dict(task)

@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    if not task.title:
        raise HTTPException(status_code=400, detail="Title required")
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (task.title, 0))
    conn.commit()
    task_id = c.lastrowid
    conn.close()
    return {"id": task_id, "title": task.title, "done": 0}

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):
    if not task.title:
        raise HTTPException(status_code=400, detail="Title required")
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE tasks SET title = ?, done = ? WHERE id = ?", (task.title, task.done, task_id))
    if c.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")
    conn.commit()
    conn.close()
    return {"id": task_id, "title": task.title, "done": task.done}

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    if c.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")
    conn.commit()
    conn.close()
    return None
