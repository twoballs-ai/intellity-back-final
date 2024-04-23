from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
import bcrypt
import os

from intellity_back_final.crud.user_crud import get_user

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
REFRESH_TOKEN_EXPIRE_DAYS = os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS")
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc)  + expires_delta
    else:
        expire = datetime.now(timezone.utc)  + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Метод для создания обновления токена
def create_refresh_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc)  + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



def authenticate_user(username: str, password: str, db):
    # Получаем пользователя по имени пользователя (email)

    user = get_user(db, username)
    print(user)
    # Если пользователь не найден, возвращаем None
    if not user:
        return None
    
    # Проверяем соответствие хэшированного пароля в базе данных с хэшированным паролем пользователя
    if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        return user  # Возвращаем пользователя, если пароль совпадает
    else:
        return None  # Возвращаем None, если пароль не совпадает
# Token verification function


def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except (jwt.JWTError, jwt.ExpiredSignatureError, jwt.DecodeError):
        raise credentials_exception