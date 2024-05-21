from sqlalchemy.orm import Session
from datetime import datetime
from intellity_back_final.crud.student_lms_crud import enroll_student_in_course, update_chapter_progress, update_module_progress, update_stage_progress
from intellity_back_final.models.course_study_lms_mopdels import CourseEnrollment, ChapterProgress, ModuleProgress, StageProgress
from typing import List, Union
import mimetypes
from sqlalchemy.exc import IntegrityError
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
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..auth import  get_user_id_by_token
import json


from intellity_back_final.models.course_editor_lms_models import Course as CourseModel, CourseCategory, Module, Stage as StageModel, Question as QuestionModel, QuizLesson as QuizLessonModel, Chapter as ChapterModel

from ..database import SessionLocal
from ..crud import teacher_lms_crud
from ..schemas import lms_schemas
from ..models.course_editor_lms_models import Chapter as ChapterModel
from intellity_back_final.models.user_models import Student
study_course_views = APIRouter()


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@study_course_views.post("/enroll/{student_id}/{course_id}")
def enroll_student(student_id: int, course_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).get(student_id)
    course = db.query(CourseModel).get(course_id)
    if not student or not course:
        raise HTTPException(status_code=404, detail="Student or Course not found")
    return enroll_student_in_course(db, student_id, course_id)

@study_course_views.post("/update_chapter/{student_id}/{chapter_id}")
def update_chapter(student_id: int, chapter_id: int, is_completed: bool, db: Session = Depends(get_db)):
    return update_chapter_progress(db, student_id, chapter_id, is_completed)

@study_course_views.post("/update_module/{student_id}/{module_id}")
def update_module(student_id: int, module_id: int, is_completed: bool, db: Session = Depends(get_db)):
    return update_module_progress(db, student_id, module_id, is_completed)

@study_course_views.post("/update_stage/{student_id}/{stage_id}")
def update_stage(student_id: int, stage_id: int, is_completed: bool, db: Session = Depends(get_db)):
    return update_stage_progress(db, student_id, stage_id, is_completed)