# FlyRank Internship — Backend Track

This repository holds my assignments for the FlyRank Internship, **Backend Track**, working toward the **Backend AI Engineer** role — the on-ramp track before transitioning into Machine Learning work.

A1 through A3 build on the same task CRUD API, swapping out one piece of real backend infrastructure at a time — same endpoints, same status codes, same JSON, only the storage underneath changes. That's what makes storage "just an implementation detail," and it's the same principle a later assignment (A15 — Layered architecture) formalizes properly.

A4 is a deliberate break from that chain: a standalone authentication project (Supabase, JWTs, protected routes) that doesn't touch the tasks API at all. It builds the "who is calling" concept that a later assignment will eventually connect back to task ownership.

A9 (BE-05) is a third, unrelated standalone project: a polite web scraper against a public practice sandbox, producing clean, schema-validated JSON from raw HTML.

## Folder structure

Each assignment lives in its **own, self-contained, independently runnable folder** — no folder is shared or overwritten between assignments:

```
FlyRank/
├── Backend Track/
│   ├── be-01-first-api/            BE-01 (A1) — in-memory CRUD API
│   ├── be-02-connect-database/     BE-02 (A2) — same API, now on SQLite
│   │   └── ai-version/             A2's AI rematch (Stage 6) — comparison only
│   ├── be-03-containerize-stack/   BE-03 (A3) — same API, now on Postgres + Docker Compose
│   │   └── ai-version/             A3's AI rematch (Stage 6) — comparison only
│   ├── be-04-auth-login-protect/   BE-04 (A4) — standalone Supabase auth API (separate project)
│   └── scraper/                    BE-05 (A9) — standalone polite web scraper (separate project)
└── AI Fluency/                     (separate track, unrelated to Backend Track)
```

| Label | Assignment | Folder | What it is |
|---|---|---|---|
| BE-01 | A1 — First API | [`Backend Track/be-01-first-api/`](Backend%20Track/be-01-first-api/) | Tasks CRUD API, in-memory storage |
| BE-02 | A2 — Connect to a database | [`Backend Track/be-02-connect-database/`](Backend%20Track/be-02-connect-database/) | Tasks CRUD API, SQLite file |
| BE-03 | A3 — Containerize your stack | [`Backend Track/be-03-containerize-stack/`](Backend%20Track/be-03-containerize-stack/) | Tasks CRUD API, PostgreSQL in Docker |
| BE-04 | A4 — Auth · Login & protect | [`Backend Track/be-04-auth-login-protect/`](Backend%20Track/be-04-auth-login-protect/) | Standalone auth API — Supabase, JWTs, protected routes (not the tasks API) |
| BE-05 | A9 — The polite scraper | [`Backend Track/scraper/`](Backend%20Track/scraper/) | Standalone scraping pipeline — fetches, parses, validates, and stores book data as JSON (not the tasks API) |

Each folder has its own README with full setup instructions and details specific to that assignment (endpoint tables, schemas, politeness rules, etc.) — this top-level README is a map, not a duplicate of that detail.

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

**BE-04 — Auth · Login & protect (Supabase)**
```bash
cd "Backend Track/be-04-auth-login-protect"
cp .env.example .env   # then fill in your own free Supabase project's URL + anon key
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python main.py
```
Requires your own free [Supabase](https://supabase.com) project — see this folder's own README for the exact setup steps. Unlike BE-01–03, this one is a standalone project with no tasks involved.

**BE-05 — The polite scraper**
```bash
cd "Backend Track/scraper"
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```
No external account or API key needed — this one only talks to a public scraping-practice sandbox. Produces `output/books.json` (60 validated records) and `output/run-report.json` (a summary of the run). Safe to re-run; it won't duplicate records, and reads previously-fetched pages from its own `cache/` folder instead of hitting the site again.

## A note on history

BE-02 and BE-03 both started from the same codebase (BE-03 is BE-02 upgraded to Postgres) — but they are kept as **separate, frozen folders** rather than one folder that got overwritten, specifically so each assignment stays independently checkable on its own, even after later work builds on top of it.
