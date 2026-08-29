import sqlite3
# pyrefly: ignore [missing-import]
from fastapi import FastAPI, HTTPException, Response, status
from contextlib import asynccontextmanager
from pydantic import BaseModel

import db as postgres_db

class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: str
    done: bool



# Define the DB file name
DB_FILE = "tasks.db"

def init_db():
    # 1. Open / Create the database file
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 2. Create the tasks table if it does not exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER DEFAULT 0
        )
    ''')

    # 3. Check if the table is empty
    cursor.execute("SELECT COUNT(*) FROM tasks")
    result = cursor.fetchone()
    
    # Bracket-free unpacking: extracts the integer from the tuple safely!
    row_count, = result if result else (0,)
    
    # 4. Seed three example tasks ONLY if the table is empty
    if row_count == 0:
        starting_tasks = (
            ("Learn FastAPI with SQLite", 0),
            ("Set up Stage 0", 1),
            ("Practice SQL queries", 0)
        )
        cursor.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)", 
            starting_tasks
        )
        print("--- Successfully seeded 3 example tasks into the database! ---")

    # 5. Commit and close the connection
    conn.commit()
    conn.close()

# FastAPI Lifespan Manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    postgres_db.init_db()
    yield

# Initialize FastAPI with lifespan handler
app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "FastAPI is connected to SQLite Database!"}

# --- STAGE 1: GET ALL TASKS ---
@app.get("/tasks")
def get_tasks():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Run the SQL command to get all tasks
    cursor.execute("SELECT id, title, done FROM tasks")
    rows = cursor.fetchall()
   
    conn.close()

    # Bracket-free mapping using tuple unpacking
    formatted_tasks = []
    for row in rows:
        task_id, title, done = row  
        formatted_tasks.append({
            "id": task_id,
            "title": title,
            "done": bool(done)
        })
    return formatted_tasks

# --- STAGE 1: GET SINGLE TASK BY ID ---
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Safely query using a parameterized placeholder
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    
    conn.close()
    
    # If the database returns no row, raise a 404 error
    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Bracket-free unpacking for a single row
    task_id, title, done = row
    return {
        "id": task_id,
        "title": title,
        "done": bool(done)
    }

# --- STAGE 2 ---
@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    # 1. Validate the input (remove trailing/leading spaces first)
    cleaned_title = task.title.strip()
    if not cleaned_title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task title cannot be empty"
        )

    # 2. Insert the task into SQLite
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # We use ? placeholders to keep our database secure!
    cursor.execute(
        "INSERT INTO tasks (title, done) values (?, ?)",
        (cleaned_title, 0) # New tasks start as uncompleted (0)
    )

    # 3. Retrieve the unique ID SQLite generated for this row
    new_id = cursor.lastrowid
    
    # Commit changes to disk and close connection
    conn.commit()
    conn.close()

    #4. Return the new task back to the client
    return {
        "id": new_id,
        "title": cleaned_title,
        "done": False
    }

# --- STAGE 3: UPDATE A TASK ---
@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):
    # 1. Validate the title input
    cleaned_title = task.title.strip()
    if not cleaned_title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Title cannot be empty"
        )
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 2. Check if the task exists first
    cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
    if cursor.fetchone() is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")

    # 3. Convert Python boolean (True/False) to SQLite integer (1/0)
    db_done = 1 if task.done else 0

    # 4. Update the task in the database
    cursor.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (cleaned_title, db_done, task_id)
    )

    conn.commit()
    conn.close()

    # 5. Return the updated task object
    return {
        "id": task_id,
        "title": cleaned_title,
        "done": task.done
    }

# --- STAGE 3: DELETE A TASK ---
@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 1. Check if the task exists first
    cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
    if cursor.fetchone() is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")

    # 2. Delete the row
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

    # 3. Return 204 No Content with an empty response body
    return Response(status_code=status.HTTP_204_NO_CONTENT)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)