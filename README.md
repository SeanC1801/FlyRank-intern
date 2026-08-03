# FlyRank API & First API Backend

This repository contains the backend API for FlyRank, alongside the initial basic FastAPI template (`be-01-first-api`).

## Progress & Purpose
- Created the FlyRank backend inside `connect-database/main.py`.
- Integrated an SQLite database (`tasks.db`) to store tasks persistently.
- Implemented CRUD (Create, Read, Update, Delete) operations for the tasks.
- Configured Uvicorn to allow the application to run on host `0.0.0.0` so it can be accessed across the local network.

## Original BE-01 API

A minimal backend with two JSON endpoints, built with FastAPI.

### Run it locally

```bash
# 1. (Recommended) create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. install dependencies
pip install -r requirements.txt

# 3. start the server
uvicorn main:app --reload
```

The server runs at http://127.0.0.1:8000

## Stage 5: Database Publishing

### Why SQLite?
SQLite was chosen because it requires zero setup, runs entirely from a single file, and allows data to survive server restarts. It's incredibly fast and great for straightforward backend applications without needing a standalone database server.

### Where is the database file?
The database file lives at `connect-database/tasks.db`. It is created automatically the first time the application runs if it doesn't already exist. We usually `.gitignore` this file so each clone of the repository gets a fresh database.

### Running the Project
To start the project, use the following commands:
```bash
cd connect-database
uvicorn main:app --reload
```

### DB Browser Screenshot
![DB Browser Screenshot](tasks_db_screenshot.png)
*(Note: Be sure to add a screenshot named `tasks_db_screenshot.png` showing the database rows in DB Browser for SQLite)*

### Example SQL Query (from Stage 4)
```sql
SELECT * FROM tasks WHERE done = 1;
```
*Returns only the tasks that have been marked as completed (done = 1).*

## Stage 6: AI vs Me (The AI Rematch)

**Prompt given to AI:**
> Write a FastAPI CRUD API using sqlite3. Create table `tasks` (id integer primary key, title text, done integer) if missing. Seed 3 tasks only when empty. 5 endpoints (GET /tasks, GET /tasks/{id}, POST /tasks, PUT /tasks/{id}, DELETE /tasks/{id}) identical to in-memory, 400/404 rules, and parameterized queries.

### Differences (AI vs Me)

1. **Better parameter binding**: The AI used `conn.row_factory = sqlite3.Row` which made reading from the database automatically convert to dictionaries, while my manual code used tuple unpacking to construct the dictionaries.
2. **Missing Lifespan Manager**: The AI put the database initialization `init_db()` loosely at the module level instead of putting it safely in an `@asynccontextmanager` lifespan event like I did.
3. **Implicit boolean casting**: My manual implementation explicitly casted `done` using `bool(done)` when sending back to the user, and converted it correctly on `PUT`. The AI simply passed the integer value `0` or `1`, which meant the response shape returned `done: 0` instead of `done: false`.
4. **Validation differences**: The AI manually checked `c.rowcount == 0` for `PUT` and `DELETE` requests to return a `404`, whereas I ran an explicit `SELECT id FROM tasks` query to check if the task existed before running the update or delete operation. Both work, but checking `rowcount` is a clever and slightly more efficient shortcut!
