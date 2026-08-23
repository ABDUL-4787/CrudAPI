from fastapi import FastAPI, Request, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security.utils import get_authorization_scheme_param
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client (gracefully handle placeholder credentials to prevent app startup crashes)
if not SUPABASE_URL or not SUPABASE_KEY or "your-project-id" in SUPABASE_URL:
    print("Warning: Valid Supabase URL or Key not set. Authentication routes will fail.")
    supabase: Client = create_client("https://placeholder.supabase.co", "placeholder-key")
else:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(
    title="Supabase Auth API Backend",
    description="FastAPI project implementing Supabase registration, login, logout, and protected routes.",
    version="1.0.0"
)

# Custom Exception for Auth Errors to bypass default FastAPI detail nesting
class AuthException(Exception):
    def __init__(self, status_code: int, error_message: str):
        self.status_code = status_code
        self.error_message = error_message

@app.exception_handler(AuthException)
async def auth_exception_handler(request: Request, exc: AuthException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.error_message}
    )

# Request validation override to return 400 Bad Request instead of 422 on payload errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Missing or invalid fields"}
    )

# Pydantic Schemas
class AuthPayload(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None

# Declare Bearer Authentication Scheme for Swagger UI Authorize lock option
security_scheme = HTTPBearer(auto_error=False)

# Reusable Authentication Dependency
def get_current_user(request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)) -> dict:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise AuthException(status_code=401, error_message="Access token required")
    
    scheme, token = get_authorization_scheme_param(auth_header)
    if scheme.lower() != "bearer" or not token:
        raise AuthException(status_code=401, error_message="Access token required")
        
    try:
        # Verify access token directly against Supabase Auth server
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            raise Exception("Invalid token user")
        
        # Save token in request state for use in logout endpoint
        request.state.token = token
        return user_response.user
    except Exception:
        raise AuthException(status_code=401, error_message="Invalid or expired token")

# Public Endpoints
@app.get("/", status_code=200)
def welcome():
    return {"message": "Welcome to the Supabase Auth API!"}

@app.get("/public/info", status_code=200)
def public_info():
    return {"message": "Welcome stranger! This info is public."}

# Authentication Endpoints
@app.post("/auth/signup", status_code=201)
def signup(payload: AuthPayload):
    if not payload.email or not payload.password:
        raise AuthException(status_code=400, error_message="Missing email or password")
    
    try:
        response = supabase.auth.sign_up({"email": payload.email, "password": payload.password})
        if not response or not response.user:
            raise Exception("Registration failed")
        
        user = response.user
        return {
            "id": user.id,
            "email": user.email,
            "created_at": user.created_at
        }
    except Exception as e:
        # Extract friendly message from Exception
        error_msg = str(e)
        raise AuthException(status_code=400, error_message=error_msg)

@app.post("/auth/login", status_code=200)
def login(payload: AuthPayload):
    if not payload.email or not payload.password:
        raise AuthException(status_code=400, error_message="Missing email or password")
        
    try:
        response = supabase.auth.sign_in_with_password({"email": payload.email, "password": payload.password})
        if not response or not response.session:
            raise Exception("Invalid credentials")
            
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token
        }
    except Exception:
        raise AuthException(status_code=401, error_message="Invalid login credentials")

@app.post("/auth/logout", status_code=204)
def logout(request: Request, current_user: dict = Depends(get_current_user)):
    token = getattr(request.state, "token", None)
    if token:
        try:
            # Authenticate the local client instance to sign out the user session
            supabase.auth.set_session(access_token=token, refresh_token=token)
            supabase.auth.sign_out()
        except Exception:
            pass
    return Response(status_code=204)

# Protected Endpoints
@app.get("/protected/profile", status_code=200)
def protected_profile(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "created_at": str(current_user.created_at)
    }

@app.get("/protected/dashboard", status_code=200)
def protected_dashboard(current_user: dict = Depends(get_current_user)):
    return {
        "message": f"Welcome to your dashboard, {current_user.email}!"
    }
