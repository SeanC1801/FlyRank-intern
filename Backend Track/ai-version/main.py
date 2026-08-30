from fastapi import FastAPI, HTTPException

import db

app = FastAPI()
db.init_db()


@app.get("/tasks")
def list_tasks():
    return db.get_all_tasks()


@app.get("/tasks/{task_id}")
def read_task(task_id: int):
    task = db.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
