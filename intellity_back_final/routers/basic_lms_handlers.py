from sqlalchemy.orm import Session
from datetime import datetime
from intellity_back_final.crud.basic_lms_crud import get_recent_courses
from intellity_back_final.crud.checker_course_lms_crud import are_all_chapters_completed, are_all_lessons_completed, are_all_modules_completed, is_course_completed
from intellity_back_final.crud.student_lms_crud import enroll_student_in_course, update_chapter_progress, update_module_progress, update_stage_progress
from intellity_back_final.models.course_study_lms_models import CourseEnrollment, ChapterProgress, ModuleProgress, StageProgress
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
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from intellity_back_final.models.course_editor_lms_models import Chapter, Module, Stage
from intellity_back_final.models.course_study_lms_models import ChapterProgress, ModuleProgress, StageProgress

basic_handle_views = APIRouter()

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@basic_handle_views.get("/recent_courses/")
def read_recent_courses(
    db: Session = Depends(get_db),
    items: int = Query(None, title="Number of Items", description="Number of recent courses to retrieve")
):
    """Function to retrieve the most recent courses.

    Args:
        db (Session, optional): The database session. Defaults to Depends(get_db).
        items (int, optional): The number of recent courses to retrieve. Defaults to None.

    Returns:
        JSONResponse: The response containing the recent courses.
    """
    recent_courses = get_recent_courses(db, items)
    courses_as_dicts = [course.to_dict() for course in recent_courses]

    return JSONResponse(
        content={
            "status": True,
            "data": courses_as_dicts,
        },
        status_code=200,
    )