from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException, Request, Depends, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
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
security = HTTPBearer(auto_error=False)

class AuthCredentials(BaseModel):
    email: str = ""
    password: str = ""

# Overriding default HTTPException handler by using a custom exception handler
# This allows us to return a JSON response instead of an HTML response
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

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

# Adding a public endpoint for GET /public/info
@app.get("/public/info")
def public_info():
    return {"message": "Welcome stranger! This info is public."}

# Helper function to get current user using token
# It checks if the token is valid and returns the user
# If the token is invalid or expired it raises an HTTPException
# Using FastAPI
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Access token required")
    
    token = credentials.credentials
    try:
        result = supabase.auth.get_user(token)
    except AuthApiError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return result.user

# Adding a protected endpoint that requires authentication
# This endpoint will return the user's profile if the token is valid
@app.get("/protected/profile")
def protected_info(user=Depends(get_current_user)):
    return { 
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at
    }

# A protected endpoint that will return the users information
@app.get("/protected/dashboard")
def protected_dashboard(user = Depends(get_current_user)):
    return {
        "message": f"Welcome {user.email} to your protected dashboard!"
    }

# Logging out
@app.post("/auth/logout", status_code=204)
def logout(user = Depends(get_current_user)):
    supabase.auth.sign_out()
    return Response(status_code=204)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ["PORT"]))