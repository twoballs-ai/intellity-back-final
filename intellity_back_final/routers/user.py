from typing import List, Union, Optional
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
    HTTPException,
    status,
    BackgroundTasks
)
from datetime import datetime, timedelta
import asyncio
from sqlalchemy import and_, func
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, EmailStr, validator
from sqlalchemy.orm import Session
import json
import jwt
import bcrypt
import os

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from intellity_back_final.models.course_editor_lms_models import Course, CourseCategory
from intellity_back_final.models.user_models import User
from ..database import SessionLocal
from ..crud import user_crud
from ..schemas import user_schemas
from intellity_back_final.utils.email_utils import send_welcome_email
from ..auth import create_access_token, create_refresh_token, verify_token, oauth2_scheme
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS", 7))
user_views = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def authenticate_user(username: str, password: str, db: Session = Depends(get_db)):
    user = user_crud.get_user_by_email(db, username)
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        return None
    return user


class UserBase(BaseModel):
    email: EmailStr

    @validator('email')
    def email_must_be_lowercase(cls, v):
        if not v.islower():
            raise ValueError('Email must be in lowercase')
        return v.lower()

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
        print(token)
        print(SECRET_KEY)
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        print(payload)
        user_id: int = payload.get("sub")
        print(user_id)
        if user_id is None:
            raise credentials_exception
        user = user_crud.get_user(db, user_id)
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

@user_views.post("/get-current-user/")
def get_current_user_view(current_user: User = Depends(get_current_user)):
    return current_user

@user_views.post("/teacher-register/")
def create_teacher_view(teacher: TeacherCreate, db: Session = Depends(get_db), background_tasks: BackgroundTasks = None):
    try:
        teacher = user_crud.create_teacher(
            db=db,
            name=teacher.name,
            lastName=teacher.lastName,
            email=teacher.email,
            password=teacher.password,
            qualification=teacher.qualification,
            skills=teacher.skills
        )
        background_tasks.add_task(send_welcome_email, teacher.email, teacher.name, "учитель")
        return JSONResponse(
            content={
                "status": True,
                "data": teacher.to_dict(),
                "message": "Вы зарегистрированы как учитель"
            },
            status_code=200,
        )
    except Exception as e:
        return JSONResponse(
            content={"status": False, "error": str(e)},
            status_code=500,
        )

@user_views.post("/student-register/")
def create_student_view(student: StudentCreate, db: Session = Depends(get_db), background_tasks: BackgroundTasks = None):
    try:
        student = user_crud.create_student(
            db=db,
            email=student.email,
            password=student.password,
            interested_categories=student.interested_categories
        )
        background_tasks.add_task(send_welcome_email, student.email, student.email.split('@')[0], "студент")  # assuming name is part of email
        return JSONResponse(
            content={
                "status": True,
                "data": student.to_dict(),
                "message": "Вы зарегистрированы как студент"
            },
            status_code=200,
        )
    except Exception as e:
        return JSONResponse(
            content={"status": False, "error": str(e)},
            status_code=500,
        )
    
@user_views.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    user = authenticate_user(form_data.username, form_data.password, db)
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
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "type": user.type
    }

@user_views.post("/token/refresh/")
async def refresh_access_token(refresh_token: str = Form(...)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_id, "type": "access"}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "Bearer"}

@user_views.get("/teacher-profile")
def get_teacher_info(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    teacher = user_crud.get_teacher_by_user_id(db, current_user.id)
    if teacher is None:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return JSONResponse(
        content={
            "status": True,
            "data": {
                "name": teacher.name,
                "last_name": teacher.lastName,
                "qualification": teacher.qualification
            },
        },
        status_code=200,
    )

@user_views.put("/teacher-profile-update")
def update_teacher_info(
    profile: user_schemas.UpdateTeacherInfo,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    teacher = user_crud.get_teacher_by_user_id(db, current_user.id)
    if teacher is None:
        raise HTTPException(status_code=404, detail="Teacher not found")

    teacher.name = profile.name
    teacher.lastName = profile.last_name
    teacher.qualification = profile.qualification

    db.commit()
    db.refresh(teacher)

    return JSONResponse(
        content={
            "status": True,
            "message": "Profile updated successfully",
            "data": {
                "name": teacher.name,
                "last_name": teacher.lastName,
                "qualification": teacher.qualification
            },
        },
        status_code=200,
    )

@user_views.put("/reset-password")
def reset_password(
    request: user_schemas.PasswordResetRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == current_user.id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if not bcrypt.checkpw(request.old_password.encode('utf-8'), user.password_hash.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    new_password_hash = bcrypt.hashpw(request.new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user.password_hash = new_password_hash

    db.commit()
    db.refresh(user)

    return JSONResponse(
        content={
            "status": True,
            "message": "Password reset successful"
        },
        status_code=200,
    )
