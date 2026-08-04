"""
OAUTH2 WITH PASSWORD BEARER AND JWT TOKENS
==========================================
This script demonstrates a full flow for:
1. Hashing and verifying passwords (using passlib).
2. Generating signed JWT Access Tokens (using pyjwt).
3. Resolving the current user using an OAuth2 Password Bearer dependency.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import jwt
from passlib.context import CryptContext

# Configuration constants
SECRET_KEY = "super-secret-development-key-dont-use-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Initialize password hashing context (using bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Tells FastAPI that token retrieval endpoint is "/token"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(title="OAuth2 & JWT Auth")

# Models
class User(BaseModel):
    username: str
    email: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

# Simulated User Database
fake_users_db = {
    "alice": {
        "username": "alice",
        "email": "alice@example.com",
        "disabled": False,
        # Hashed password for: "wonderland"
        "hashed_password": pwd_context.hash("wonderland"),
    }
}

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Current User Dependency
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    user_dict = fake_users_db.get(username)
    if user_dict is None:
        raise credentials_exception
    return User(**user_dict)

# Endpoints

# 1. Login / Token generation endpoint
# OAuth2PasswordRequestForm is form-encoded: client posts username and password
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict or not verify_password(form_data.password, user_dict["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# 2. Protected endpoint returning the active user info
@app.get("/users/me", response_model=User)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# To run this file:
# uvicorn 05_security_and_auth.02_oauth2_jwt:app --reload
