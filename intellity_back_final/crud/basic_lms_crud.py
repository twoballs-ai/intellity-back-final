from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException
from sqlalchemy import asc, create_engine
from sqlalchemy.orm import sessionmaker

from ..models.course_editor_lms_models import Course
from ..schemas import lms_schemas
from typing import List

# def get_user(db: Session, user_id: int):
#     return db.query(models.User).filter(models.User.id == user_id).first()


# def get_user_by_email(db: Session, email: str):
#     return db.query(models.User).filter(models.User.email == email).first()

from sqlalchemy.orm import Session
from datetime import datetime
from ..models.course_study_lms_models import CourseEnrollment, ChapterProgress, ModuleProgress, StageProgress

def get_recent_courses(db: Session):
    return db.query(Course).order_by(Course.id.desc()).limit(8).all()