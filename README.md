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
