# FlyRank Internship — Backend Track

This repository holds my assignments for the FlyRank Internship, **Backend Track**, working toward the **Backend AI Engineer** role, the on-ramp track before transitioning into Machine Learning work.

Each assignment builds on the same task CRUD API, swapping out one piece of real backend infrastructure at a time:

| Assignment | What it adds | Storage |
|---|---|---|
| A1 — First API | The API itself: routes, request/response shapes | In-memory (list) |
| A2 — Connect to a database | Real persistence across restarts | SQLite file |
| A3 — Containerize your stack | Docker, Postgres, Docker Compose, `.env` secrets | PostgreSQL (in Docker) |

The lesson threading through all three: the API's behavior never changes — same endpoints, same status codes, same JSON — only what's running underneath it does. That's what makes storage "just an implementation detail," and it's the same principle a later assignment (A15 — Layered architecture) formalizes properly.

---

## [BE-01] First API (`be-01-first-api/`)

A minimal backend with two JSON endpoints, built with FastAPI. It serves as the foundation for future assignments.

### Running BE-01
```bash
# 1. (Recommended) create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. install dependencies
pip install -r requirements.txt

# 3. start the server
cd be-01-first-api
uvicorn main:app --reload
```
The server runs at http://127.0.0.1:8000

---

## [BE-02 / A3] Containerize your stack (`be-02-connect-database/`)

This folder has evolved across three assignments: it started as A1's in-memory API, gained SQLite persistence in A2, and now runs the full CRUD API against a real **PostgreSQL** server — with the entire stack (API + database) started by a single command via **Docker Compose**.

### Current stack
- **FastAPI** — the API layer (unchanged in behavior since A1)
- **PostgreSQL 18**, running in its own Docker container, not installed on the host machine
- **psycopg** — the Python driver talking to Postgres, using parameterized queries throughout
- **Docker Compose** — orchestrates the `api` and `db` containers together on a shared network
- **A named Docker volume** (`taskdata`) — keeps database rows alive across container restarts and rebuilds

### Running it
```bash
cd be-02-connect-database
cp .env.example .env
docker compose up
```
The API is available at http://localhost:8000 — no manual Postgres installation or setup required.

### Where the data actually lives
Not in a file on disk anymore (that was A2's SQLite approach) — it's inside the `taskdata` Docker volume, managed by Postgres running in the `db` container. See `be-02-connect-database/README.md` for the full endpoint table, environment variables, and a screenshot of the live data.

### Stage 6: AI vs Me (The AI Rematch)

**Prompt given to AI:**
> Write a FastAPI CRUD API using sqlite3. Create table `tasks` (id integer primary key, title text, done integer) if missing. Seed 3 tasks only when empty. 5 endpoints (GET /tasks, GET /tasks/{id}, POST /tasks, PUT /tasks/{id}, DELETE /tasks/{id}) identical to in-memory, 400/404 rules, and parameterized queries.

*(This comparison was run during the A2/SQLite stage — kept here as a record of that exercise.)*

#### Differences (AI vs Me)

1. **Better parameter binding**: The AI used `conn.row_factory = sqlite3.Row` which made reading from the database automatically convert to dictionaries, while my manual code used tuple unpacking to construct the dictionaries.
2. **Missing Lifespan Manager**: The AI put the database initialization `init_db()` loosely at the module level instead of putting it safely in an `@asynccontextmanager` lifespan event like I did.
3. **Implicit boolean casting**: My manual implementation explicitly casted `done` using `bool(done)` when sending back to the user, and converted it correctly on `PUT`. The AI simply passed the integer value `0` or `1`, which meant the response shape returned `done: 0` instead of `done: false`.
4. **Validation differences**: The AI manually checked `c.rowcount == 0` for `PUT` and `DELETE` requests to return a `404`, whereas I ran an explicit `SELECT id FROM tasks` query to check if the task existed before running the update or delete operation. Both work, but checking `rowcount` is a clever and slightly more efficient shortcut!
