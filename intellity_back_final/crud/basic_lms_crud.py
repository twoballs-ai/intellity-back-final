from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException
from sqlalchemy import asc, create_engine
from sqlalchemy.orm import sessionmaker

from ..models.course_editor_lms_models import Course
from ..schemas import lms_schemas
from typing import List

from sqlalchemy.orm import Session
from datetime import datetime
from ..models.course_study_lms_models import CourseEnrollment, ChapterProgress, ModuleProgress, StageProgress

def get_recent_courses(db: Session, items: int = None):
    query = db.query(Course).order_by(Course.id.desc())
    if items:
        query = query.limit(items)
    else:
        query = query # Default to 8 if no items parameter is provided
    return query.all()