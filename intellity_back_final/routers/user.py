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

from intellity_back_final.models.lms_models import Course, CourseCategory
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
from ..auth import  authenticate_user, create_access_token, create_refresh_token, verify_token

from pydantic import BaseModel



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/token")
SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")
REFRESH_TOKEN_EXPIRE_DAYS = os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS")
user_views = APIRouter()


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()




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
        
        
@user_views.post("/get-current-user/")
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Here you can fetch the current user based on the username
    # For example, user = get_user(username)
    # Or if you're using OAuth2 with supported user identifiers, you can simply return the username
    
    # Return the current user
    return username

@user_views.post("/teacher-register/")
def create_teacher_view(teacher: TeacherCreate, db: Session = Depends(get_db)):
    """
    Регистрирует нового учителя.
    """
    teacher = user_crud.create_teacher(db=db, name=teacher.name,lastName = teacher.lastName, email=teacher.email, password=teacher.password, qualification=teacher.qualification, skills=teacher.skills)
    # Вызываем функцию create_teacher, передавая ей данные из teacher
    return teacher

@user_views.post("/student-register/")
def create_student_view(student: StudentCreate, db: Session = Depends(get_db)):
    """
    Регистрирует нового студента.
    """
    student = user_crud.create_student(db=db,  email=student.email, password=student.password, interested_categories=student.interested_categories)
    return student


@user_views.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password,db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"sub": user.email, "type": "access"}, expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(minutes=int(REFRESH_TOKEN_EXPIRE_DAYS))
    refresh_token = create_refresh_token(
        data={"sub": user.email, "type": "refresh"}, expires_delta=refresh_token_expires
    )
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "Bearer", "user_id": user.id, "type":user.type}



# Метод для обновления токена доступа с использованием токена обновления
@user_views.post("/token/refresh")
async def refresh_access_token(refresh_token: str = Form(...)):
    verify_token(refresh_token, HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    ))
    payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    username: str = payload.get("sub")
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"sub": username, "type": "access"}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "Bearer"}


