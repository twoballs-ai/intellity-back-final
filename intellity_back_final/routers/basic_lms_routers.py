from sqlalchemy.orm import Session
from datetime import datetime
from intellity_back_final.crud.basic_lms_crud import get_courses_by_cat, get_recent_courses
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

import json


from intellity_back_final.models.course_editor_lms_models import Course as CourseModel, CourseCategory, Module, Stage as StageModel,  QuizLesson as QuizLessonModel, Chapter as ChapterModel

from ..database import SessionLocal
from ..crud import teacher_lms_crud
from ..schemas import lms_schemas
from ..models.course_editor_lms_models import Chapter as ChapterModel
from intellity_back_final.models.user_models import Student
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
from intellity_back_final.models.course_editor_lms_models import Chapter, Module, Stage
from intellity_back_final.models.course_study_lms_models import ChapterProgress, ModuleProgress, StageProgress


logger = logging.getLogger(__name__)

basic_handle_views = APIRouter()

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@basic_handle_views.get("/category/")
def read_course_categories(skip: int = 0, limit: int = 100, to_select: bool = False, db: Session = Depends(get_db)) -> JSONResponse:
    """
    Retrieve a list of course categories.

    Args:
        skip (int, optional): Number of categories to skip. Defaults to 0.
        limit (int, optional): Maximum number of categories to return. Defaults to 100.
        to_select (bool, optional): Whether to return a simplified selection. Defaults to False.
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Returns:
        JSONResponse: A JSON response containing the status and data.
    """
    try:
        response_data = teacher_lms_crud.get_categoryes(db, skip=skip, limit=limit, to_select=to_select)

        return JSONResponse(
            content={
                "status": True,
                "data": response_data,
            },
            status_code=200,
        )
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
        

@basic_handle_views.get("/course/")
def read_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(CourseModel).filter(CourseModel.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    chapters = db.query(ChapterModel).filter(ChapterModel.course_id == course_id).all()
    
    course_data = course.to_dict()
    course_data["chapters"] = [{"title": chapter.title, "description": chapter.description} for chapter in chapters]
    
    return JSONResponse(
        content={
            "status": True,
            "data": course_data,
        },
        status_code=200,
    )

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


@basic_handle_views.get("/courses-by-cat/")
def read_courses(skip: int = 0, limit: int = 100, category_id: Optional[int] = None, db: Session = Depends(get_db)):
    courses = get_courses_by_cat(db, skip=skip, limit=limit, category_id=category_id)
    list_courses =[course.to_dict() for course in courses]
    return JSONResponse(
        content={
            "status": True,
            "data": list_courses,
        },
        status_code=200,
    )
