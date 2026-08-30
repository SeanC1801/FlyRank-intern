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
