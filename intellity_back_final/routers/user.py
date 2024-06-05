from typing import List, Union
import mimetypes
from fastapi import (
    APIRouter,
    Depends,
    WebSocket,
    Form,
    Query,
    File,
    UploadFile,
    Response,
    HTTPException
)
from datetime import datetime
from typing import List, Optional
import asyncio
from sqlalchemy import and_, func
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session

import json

from intellity_back_final.models.course_editor_lms_models import Course, CourseCategory
from intellity_back_final.models.user_models import User
from ..database import SessionLocal
from ..crud import user_crud
from ..schemas import lms_schemas

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
import bcrypt
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
import os
from ..auth import create_access_token, create_refresh_token, verify_token, oauth2_scheme

from pydantic import BaseModel


SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS", 7))
user_views = APIRouter()


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def authenticate_user(username: str, password: str, db: Session = Depends(get_db)):
    user = user_crud.get_user_by_email(db, username)
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        return None
    return user


class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class TeacherCreate(UserCreate):
    qualification: str
    name: str
    lastName: str
    skills: str

class Teacher(TeacherCreate):
    id: int

    class Config:
        orm_mode = True

class StudentCreate(UserCreate):
    interested_categories: str

class Student(StudentCreate):
    id: int

    class Config:
        orm_mode = True
        

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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
        user = user_crud.get_user(db, user_id)
        if user is None:
            raise credentials_exception
        return user
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.DecodeError:
        raise credentials_exception



@user_views.post("/get-current-user/")
def get_current_user_view(current_user: User = Depends(get_current_user)):
    return current_user

@user_views.post("/teacher-register/")
def create_teacher_view(teacher: TeacherCreate, db: Session = Depends(get_db)):
    teacher = user_crud.create_teacher(db=db, name=teacher.name, lastName=teacher.lastName, email=teacher.email, password=teacher.password, qualification=teacher.qualification, skills=teacher.skills)
    return teacher

@user_views.post("/student-register/")
def create_student_view(student: StudentCreate, db: Session = Depends(get_db)):
    student = user_crud.create_student(db=db, email=student.email, password=student.password, interested_categories=student.interested_categories)
    return student

@user_views.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    print(user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "type": "access"}, expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={"sub": user.id, "type": "refresh"}, expires_delta=refresh_token_expires
    )
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "Bearer", "type": user.type}

@user_views.post("/token/refresh/")
async def refresh_access_token(refresh_token: str = Form(...)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Verify and decode the refresh token
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    # Create new access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_id, "type": "access"}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "Bearer"}