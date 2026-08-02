# BE-01 — My First API

A minimal backend with two JSON endpoints, built with FastAPI.

## Run it locally

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

## Endpoints

| Method | Path            | Example response                                      |
|--------|-----------------|-------------------------------------------------------|
| GET    | `/`             | `{"message": "Hello from my first backend!"}`         |
| GET    | `/greet/{name}` | `{"greeting": "Hello, sean!", "endpoint": "greet"}`   |

Interactive docs (auto-generated): http://127.0.0.1:8000/docs

## Try it with curl

```bash
curl http://127.0.0.1:8000/
curl http://127.0.0.1:8000/greet/sean
```
