# Task API (ai-version)

A small FastAPI task-tracking API backed by Postgres, fully containerized
with Docker Compose.

## Run it

```bash
cp .env.example .env
docker compose up -d --build
```

That's it — one command brings up Postgres and the API together. The API
waits for Postgres to report healthy (via a `pg_isready` healthcheck)
before it starts, so there's no startup race.

API is available at `http://localhost:8001`.

## Environment variables

See [`.env.example`](.env.example). `DATABASE_URL` is the only variable
required, e.g.:

```
DATABASE_URL=postgresql://taskuser:taskpass@localhost:5433/taskdb
```

Inside `docker compose`, the API container talks to Postgres over the
compose network using the service name `db`, so its `DATABASE_URL` is set
directly in `compose.yaml` (`db:5432`) rather than from `.env`.

`.env` is git-ignored; only `.env.example` is committed.

## Endpoints

| Method | Path            | Description                        | Success | Errors |
|--------|-----------------|------------------------------------|---------|--------|
| GET    | `/tasks`        | List all tasks                     | 200     | —      |
| GET    | `/tasks/{id}`   | Get one task by id                 | 200     | 404    |
| POST   | `/tasks`        | Create a task                      | 201     | —      |
| PUT    | `/tasks/{id}`   | Update a task's title/done         | 200     | 404    |
| DELETE | `/tasks/{id}`   | Delete a task                      | 204     | 404    |
| GET    | `/health`       | Postgres connectivity check        | 200     | 503    |

## Example

```bash
$ curl -i localhost:8001/tasks
HTTP/1.1 200 OK
content-type: application/json

[{"id":1,"title":"Buy groceries","done":false},{"id":2,"title":"Write report","done":false},{"id":3,"title":"Walk the dog","done":true},{"id":4,"title":"Persistence check","done":false}]
```

## Data persistence

Postgres data lives in a named Docker volume (`taskdata`), not in the
container itself. `docker compose down && docker compose up -d` will
restart both containers with the same data intact. Verified by creating a
task, tearing the stack down, bringing it back up, and confirming the row
survived.

## Local development (without Docker)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Requires a reachable Postgres instance matching `DATABASE_URL` in `.env`.
