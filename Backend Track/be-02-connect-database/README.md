# Task CRUD API — Postgres + Docker

A simple task management API (FastAPI + PostgreSQL) fully containerized with Docker Compose.
Same API from A1 (in-memory) and A2 (SQLite) — this time backed by a real Postgres server running in its own container.

## Run it

```bash
cp .env.example .env
docker compose up
```

That's it — the API and its database start together. The API is available at `http://localhost:8000`.

## Environment variables

Copy `.env.example` to `.env` before running. It sets one variable:

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Postgres connection string (user, password, host, port, database name) |

The values already match what `compose.yaml` expects — no changes needed to run locally.

## Endpoints

| Method | Path | Description | Success | Errors |
|---|---|---|---|---|
| GET | `/tasks` | List all tasks | 200 | — |
| GET | `/tasks/{id}` | Get one task by id | 200 | 404 if not found |
| POST | `/tasks` | Create a task | 201 | 400 if title empty |
| PUT | `/tasks/{id}` | Update a task's title/done | 200 | 400 if title empty, 404 if not found |
| DELETE | `/tasks/{id}` | Delete a task | 204 | 404 if not found |

## Example request

```
$ curl -i http://localhost:8000/tasks

HTTP/1.1 200 OK
content-type: application/json

[{"id":1,"title":"Learn FastAPI with Postgres","done":false},{"id":2,"title":"Set up Stage 1","done":true},{"id":3,"title":"Practice parametrized queries","done":false}]
```

## Data in the database

![Postgres data](./db-screenshot.png)

## Persistence

Data lives in a named Docker volume (`taskdata`), not inside the containers themselves. Running `docker compose down` followed by `docker compose up` again brings everything back with the same data — the containers are disposable, the volume is not.

## Stage 6: AI vs Me (The AI Rematch)

The AI's version lives in `../ai-version/` — a separate folder, never touching this one, so this hand-built stack stays the actual submission.

**My prompt to the AI:**
> Your CRUD API will not change, HTTP Methods including its: GET /tasks, POST /tasks, PUT /tasks/:id, DELETE /tasks/:id, and JSON responses are still identical. The underlying data storage from W2 will upgrade from SQLite files into rows inside PostgreSQL
> We will only work with the Database container and the Docker system including:
> [Docker Image: A frozen, pre-built template containing the database engine and everything it needs to run. For this task, you are using the official postgres image directly rather than creating your own build recipe.]
> [Docker Container: The live, isolated process running that PostgreSQL image as an independent database server.]
> [Docker Volume: Dedicated disk space managed by Docker that outlives the container, ensuring your database tables and rows survive restarts and teardowns.]
> [compose.yaml (or docker-compose.yml): The blueprint file that defines your services, connects your app and database, attaches the persistent volume, and pulls environment variables into the container stack with a single command.]
> [.env: A separate configuration file holding sensitive credentials (POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, port configs) kept out of version control so connection secrets stay secure and easily configurable across environments.]
>
> Documentation: *(full stage-by-stage log of how I built the hand-written version, given to the AI as reference context — see the earlier sections of this README and the commit history for the same content)*
>
> Help me do this project, DO NOT access any folders but the ai-version folder. Follow it as it is

### What actually happened when I ran it

I didn't just read the AI's code — I ran it, hit its endpoints with `curl`, and checked the database directly, the same way I tested my own version.

**Worked correctly, first try:** `docker compose up` on a completely fresh volume brought up both containers with no crash — the AI included a `pg_isready` healthcheck and `depends_on: condition: service_healthy` from the start. My own version needed a second pass: my first `compose.yaml` used a plain `depends_on: [db]`, which only waits for the container to *start*, not for Postgres to actually be ready — I hit a real crash on a fresh clone and had to add the healthcheck fix afterward.

**Persistence: verified true.** I created a task, ran `docker compose down` then `up` again, and the task survived — same as mine.

**A real bug I found by testing, not just reading:** `POST /tasks` with an empty title returns `201 Created` with the empty title saved, instead of `400`. The AI's `add_task()` route has **no validation at all** — it passes whatever `title` it receives straight into the database. My version explicitly checks for and rejects an empty/whitespace-only title with a `400` before touching the database.

**Same mistake I originally made:** its error responses are shaped `{"detail": "Task not found"}`, not `{"error": ...}` — the assignment's spec explicitly asks for `{"error": ...}`. I made this exact same mistake at first (FastAPI's default `HTTPException` behavior does this automatically) and only caught it on a careful re-check against the requirements; the AI never corrected it.

### What it did better

- **Pinned the Postgres version** (`postgres:18`) instead of my unpinned `image: postgres`, which floats to whatever "latest" resolves to at pull time — a real reproducibility improvement.
- **Included the healthcheck/`depends_on: condition: service_healthy` fix from the start**, avoiding the startup race condition I only caught after testing on a fresh clone.
- Used `with` context managers for both the connection and cursor in every `db.py` function, which auto-commits/closes — slightly cleaner than my explicit `conn.commit()` / `conn.close()` pairs, though functionally equivalent.

### What it got wrong or ignored

- **No input validation** — the missing `400` for an empty title is a genuine functional bug, not a style difference.
- **Wrong error response shape** — `{"detail": ...}` instead of the spec's `{"error": ...}`.

### What my prompt forgot to specify

Looking back at my own prompt: **I never told it about the 400/empty-title validation rule at all.** I described the five endpoints and the storage upgrade in detail, but never stated the validation requirement explicitly — and the AI's output reflects exactly that gap. This is the core lesson of this stage: the AI didn't fail on its own, it faithfully built what I specified, and what I specified was incomplete.

### One rematch

Regenerating with an explicit instruction — *"reject an empty or whitespace-only title with a 400 Bad Request, and shape every error response as `{\"error\": \"<message>\"}` instead of FastAPI's default `{\"detail\": ...}`"* — would very likely fix both gaps found here, since neither is a hard problem, just an unstated requirement.
