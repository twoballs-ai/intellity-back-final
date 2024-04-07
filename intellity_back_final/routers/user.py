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

from ..database import SessionLocal
from ..crud import user_crud
from ..schemas import lms_schemas

user_views = APIRouter()


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@user_views.post("/teacher-register/")
def create_teacher(qualification:str, skills:str,db: Session = Depends(get_db)):
    return user_crud.create_teacher(db=db, qualification=qualification, skills=skills)

@user_views.post("/student-register/")
def create_student(interested_categories:str,db: Session = Depends(get_db)):
    return user_crud.create_student(db=db, interested_categories=interested_categories)