from sqlalchemy.orm import Session
from datetime import datetime
from intellity_back_final.crud import student_lms_crud
from intellity_back_final.crud.student_lms_crud import enroll_student_in_course, get_course_enrollment, update_chapter_progress, update_module_progress, update_stage_progress
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

from intellity_back_final.routers.user import get_current_user
import json


from intellity_back_final.models.course_editor_lms_models import Course as CourseModel, CourseCategory, Module, Stage as StageModel,  QuizLesson as QuizLessonModel, Chapter as ChapterModel

from ..database import SessionLocal
from ..crud import teacher_lms_crud
from ..schemas import lms_schemas
from ..models.course_editor_lms_models import Chapter as ChapterModel, QuizLesson
from intellity_back_final.models.user_models import Student, User
study_course_views = APIRouter()


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@study_course_views.get("/student/courses")
def get_enrolled_courses(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    enrollments = db.query(CourseEnrollment).filter(CourseEnrollment.student_id == current_user.id).all()
    if not enrollments:
        raise HTTPException(status_code=404, detail="Student not found or not enrolled in any courses")
    courses = [enrollment.course_model.to_dict()  for enrollment in enrollments]
    return JSONResponse(
        content={
            "status": True,
            "data": courses,
        },
        status_code=200,
    )


@study_course_views.get("/check-enrollment/")
def check_enrollment(course_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    student_id = current_user.id  # Извлечение student_id из текущего пользователя
    enrollment = db.query(CourseEnrollment).filter_by(course_id=course_id, student_id=student_id).first()
    
    if enrollment:
        return JSONResponse(
            content={
                "status": "True",
                "data": enrollment.to_dict(),
                "enrolled_status":"enrolled"
            },
            status_code=200,
        )

    else:
        raise HTTPException(status_code=404, detail="Enrollment not found")




@study_course_views.post("/enroll/{course_id}")
def enroll_student(course_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    student = db.query(Student).get(current_user.id)
    course = db.query(CourseModel).get(course_id)
    if not student or not course:
        raise HTTPException(status_code=404, detail="Student or Course not found")
    
    enrollment = get_course_enrollment(db, student.id, course_id)
    if enrollment:
        return JSONResponse(
            content={
                "status": False,
                "data": "Student is already enrolled in this course"
            },
            status_code=400,
        )

    enroll = enroll_student_in_course(db, student.id, course_id)
    return JSONResponse(
        content={
            "status": True,
            "data": enroll.to_dict(),
        },
        status_code=200,
    )

@study_course_views.post("/update_chapter/{student_id}/{chapter_id}")
def update_chapter(student_id: int, chapter_id: int, is_completed: bool, db: Session = Depends(get_db)):
    return update_chapter_progress(db, student_id, chapter_id, is_completed)

@study_course_views.post("/update_module/{student_id}/{module_id}")
def update_module(student_id: int, module_id: int, is_completed: bool, db: Session = Depends(get_db)):
    return update_module_progress(db, student_id, module_id, is_completed)

@study_course_views.post("/update_stage/{student_id}/{stage_id}")
def update_stage(student_id: int, stage_id: int, is_completed: bool, db: Session = Depends(get_db)):
    return update_stage_progress(db, student_id, stage_id, is_completed)


@study_course_views.get("/stage/{stage_id}")
def read_stage(stage_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Retrieve the stage
    stage = student_lms_crud.get_stage_for_student(db, stage_id=stage_id)
    
    if stage is None:
        raise HTTPException(status_code=404, detail="Stage not found")
    
    # Retrieve the course ID
    course_id = None
    if stage.module:
        course_id = stage.module.chapter.course_id
    # Verify if the student is enrolled in the course corresponding to the stage
    course_enrollment = db.query(CourseEnrollment).filter(
        CourseEnrollment.course_id == course_id,
        CourseEnrollment.student_id == current_user.id
    ).first()
    
    if not course_enrollment:
        raise HTTPException(status_code=403, detail="You are not enrolled in this course")
    
    # Format the data based on the stage type
    if isinstance(stage, QuizLesson):
        stage_data = stage.to_learn_dict()
    else:
        stage_data = stage.to_dict()
    
    # Return the formatted data as a JSON response
    return JSONResponse(
        content={
            "status": True,
            "data": stage_data,
        },
        status_code=200,
    )