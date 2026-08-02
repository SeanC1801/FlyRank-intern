from fastapi import FastAPI

# This `app` object IS your server. Every endpoint hangs off it.
app = FastAPI(title="BE-01 First API")


# Endpoint 1: the "root". Visit http://127.0.0.1:8000/ and you hit this.
@app.get("/")
def read_root():
    # Whatever you return, FastAPI converts to JSON automatically.
    return {"message": "Hello from my first backend!"}


# Endpoint 2: a dynamic endpoint. The {name} in the path becomes an argument.
# http://127.0.0.1:8000/greet/sean  ->  name = "sean"
@app.get("/greet/{name}")
def greet(name: str):
    return {"greeting": f"Hello, {name}!", "endpoint": "greet"}
