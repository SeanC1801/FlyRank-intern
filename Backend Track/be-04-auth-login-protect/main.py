from fastapi import FastAPI, HTTPException
import os
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from supabase import create_client, Client
# pyrefly: ignore [missing-import]
from supabase_auth.errors import AuthApiError
from pydantic import BaseModel

load_dotenv()

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_ANON_KEY = os.environ['SUPABASE_ANON_KEY']

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

app = FastAPI()

class AuthCredentials(BaseModel):
    email: str = ""
    password: str = ""

# When there is a missing email or password program should raise an error when SIGNING UP
@app.post("/auth/signup", status_code=201)
def signup(creds: AuthCredentials):
    if not creds.email or not creds.password:
        raise HTTPException(status_code=400, detail="Missing email or password")

    result = supabase.auth.sign_up({"email": creds.email, "password": creds.password})
    return result.user

# When logging in the authentication
@app.post("/auth/login")
def login(creds: AuthCredentials):
    if not creds.email or not creds.password:
        raise HTTPException(status_code=400, detail="Missing email or password")
    
    try:
        result = supabase.auth.sign_in_with_password({"email": creds.email, "password": creds.password})
    except AuthApiError:
        raise HTTPException(status_code=401, detail="Invalid login credentials")

    return {
        "access_token": result.session.access_token,
        "refresh_token": result.session.refresh_token
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ["PORT"])) 