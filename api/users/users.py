import json

# Datetime
from datetime import datetime, timedelta
from typing import Annotated, List

# FastAPI
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer

# Security
from jose import JWTError, jwt
from passlib.context import CryptContext

# Pydantic
from pydantic import BaseModel

# Security Params
SECRET_KEY = "06ebb2d8520b459a83dbfc7f71dae8c8e1d8bcf8504bb34e1116a5e6c273afe0"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10080

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    user_id: int
    username: str | None = None
    displayname: str | None = None
    email: str | None = None

class UserInDB(User):
    hashed_password: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, user_id: int):
    if user_id in db:
        user_dict = db[user_id]
        return UserInDB(**user_dict)
    
def authenticate_user(data, username: str, password: str):
    user = get_user(data, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user