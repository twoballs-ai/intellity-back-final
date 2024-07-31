from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
import bcrypt
import os
from fastapi import Header
# from .main import oauth2_scheme
from intellity_back_final.crud import user_crud
from intellity_back_final.crud.user_crud import get_user
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from intellity_back_final.database import SessionLocal
from intellity_back_final.models.user_models import SiteUser, User
load_dotenv()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/token")

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS", 7))

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        user_type: str = payload.get("type")
        roles: list = payload.get("roles", [])
        if user_id is None:
            raise credentials_exception
        return {"user_id": user_id, "user_type": user_type, "roles": roles}
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.DecodeError:
        raise credentials_exception
    

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # print(token)
        # print(SECRET_KEY)
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        # print(payload)
        user_id: int = payload.get("sub")
        # print(user_id)
        if user_id is None:
            raise credentials_exception
        user = user_crud.get_user(db, user_id)
        if user is None:
            raise credentials_exception
        print(user)
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user_role(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user = get_user(db, user_id)
        if user is None:
            raise credentials_exception
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
def type_checker(required_types: list):
    def type_dependency(current_user: dict = Depends(get_current_user)):
        user_type = current_user.get("user_type", "")
        if user_type not in required_types:
            raise HTTPException(
                status_code=403,
                detail="Operation not permitted",
            )
        return current_user
    return type_dependency

def role_checker(required_roles: list):
    async def role_dependency(current_user: User = Depends(get_current_user)):
        print(f"Checking roles for user: {current_user}")
        if isinstance(current_user, SiteUser):
            print(f"User is a SiteUser with roles: {current_user.role.name if current_user.role else 'No role'}")
            user_roles = [current_user.role.name] if current_user.role else []
            if not any(role in user_roles for role in required_roles):
                print(f"User does not have the required role(s): {required_roles}")
                raise HTTPException(
                    status_code=403,
                    detail="Operation not permitted",
                )
            return current_user
        else:
            raise HTTPException(
                    status_code=403,
                    detail="Operation not permitted",
                )
    return role_dependency