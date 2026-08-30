from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import db

app = FastAPI()
db.init_db()


@app.get("/health")
def health_check():
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        return {"status": "ok", "db": "ok"}
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "db": "unreachable"},
        )


class TaskCreate(BaseModel):
    title: str
    done: bool = False


class TaskUpdate(BaseModel):
    title: str
    done: bool


@app.get("/tasks")
def list_tasks():
    return db.get_all_tasks()


@app.get("/tasks/{task_id}")
def read_task(task_id: int):
    task = db.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.post("/tasks", status_code=201)
def add_task(task: TaskCreate):
    return db.create_task(task.title, task.done)


@app.put("/tasks/{task_id}")
def edit_task(task_id: int, task: TaskUpdate):
    updated = db.update_task(task_id, task.title, task.done)
    if updated is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated


@app.delete("/tasks/{task_id}", status_code=204)
def remove_task(task_id: int):
    deleted = db.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return Response(status_code=204)
