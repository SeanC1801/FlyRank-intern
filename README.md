# FlyRank Internship — Backend Track

This repository holds my assignments for the FlyRank Internship, **Backend Track**, working toward the **Backend AI Engineer** role — the on-ramp track before transitioning into Machine Learning work.

Each assignment builds on the same task CRUD API, swapping out one piece of real backend infrastructure at a time — same endpoints, same status codes, same JSON, only the storage underneath changes. That's what makes storage "just an implementation detail," and it's the same principle a later assignment (A15 — Layered architecture) formalizes properly.

## Folder structure

Each assignment lives in its **own, self-contained, independently runnable folder** — no folder is shared or overwritten between assignments:

```
FlyRank/
├── Backend Track/
│   ├── be-01-first-api/            BE-01 (A1) — in-memory CRUD API
│   ├── be-02-connect-database/     BE-02 (A2) — same API, now on SQLite
│   │   └── ai-version/             A2's AI rematch (Stage 6) — comparison only
│   └── be-03-containerize-stack/   BE-03 (A3) — same API, now on Postgres + Docker Compose
│       └── ai-version/             A3's AI rematch (Stage 6) — comparison only
└── AI Fluency/                     (separate track, unrelated to Backend Track)
```

| Label | Assignment | Folder | Storage |
|---|---|---|---|
| BE-01 | A1 — First API | [`Backend Track/be-01-first-api/`](Backend%20Track/be-01-first-api/) | In-memory (list) |
| BE-02 | A2 — Connect to a database | [`Backend Track/be-02-connect-database/`](Backend%20Track/be-02-connect-database/) | SQLite file |
| BE-03 | A3 — Containerize your stack | [`Backend Track/be-03-containerize-stack/`](Backend%20Track/be-03-containerize-stack/) | PostgreSQL, in Docker |

Each folder has its own README with full setup instructions, an endpoint table, and its own "AI vs me" Stage 6 comparison — this top-level README is a map, not a duplicate of that detail.

## Setting up each one

They don't share a virtual environment or dependencies — set each one up independently, from inside its own folder:

**BE-01 — First API**
```bash
cd "Backend Track/be-01-first-api"
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

**BE-02 — Connect to a database (SQLite)**
```bash
cd "Backend Track/be-02-connect-database"
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

**BE-03 — Containerize your stack (Postgres + Docker)**
```bash
cd "Backend Track/be-03-containerize-stack"
cp .env.example .env
docker compose up
```
No local Python setup needed for BE-03 — Docker builds and runs everything, including Postgres itself.

## A note on history

BE-02 and BE-03 both started from the same codebase (BE-03 is BE-02 upgraded to Postgres) — but they are kept as **separate, frozen folders** rather than one folder that got overwritten, specifically so each assignment stays independently checkable on its own, even after later work builds on top of it.
