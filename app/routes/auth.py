from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.auth import get_password_hash, verify_password, create_access_token
from app.database import get_db
from app.schemas import UserAuth, UserResponse, Token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserAuth):
    with get_db() as conn:
        with conn.cursor() as cursor:
            # Check if email exists
            cursor.execute("SELECT id FROM users WHERE email = %s;", (user_in.email,))
            if cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered."
                )
            
            hashed_pwd = get_password_hash(user_in.password)
            cursor.execute(
                "INSERT INTO users (email, hashed_password) VALUES (%s, %s) RETURNING id, email;",
                (user_in.email, hashed_pwd)
            )
            new_user = cursor.fetchone()
            conn.commit()
            return new_user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    email = form_data.username.lower().strip()
    password = form_data.password
    
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, email, hashed_password FROM users WHERE email = %s;", (email,))
            user = cursor.fetchone()
            
            if not user or not verify_password(password, user["hashed_password"]):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password."
                )
            
            access_token = create_access_token(data={"sub": str(user["id"])})
            return {"access_token": access_token, "token_type": "bearer"}
