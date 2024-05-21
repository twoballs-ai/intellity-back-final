from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException
from sqlalchemy import asc, create_engine
from sqlalchemy.orm import sessionmaker

from ..models import course_editor_lms_models
from ..schemas import lms_schemas
from typing import List

# def get_user(db: Session, user_id: int):
#     return db.query(models.User).filter(models.User.id == user_id).first()


# def get_user_by_email(db: Session, email: str):
#     return db.query(models.User).filter(models.User.email == email).first()

from sqlalchemy.orm import Session
from datetime import datetime
from ..models.course_study_lms_mopdels import CourseEnrollment, ChapterProgress, ModuleProgress, StageProgress

def enroll_student_in_course(db: Session, student_id: int, course_id: int):
    enrollment = CourseEnrollment(
        student_id=student_id,
        course_id=course_id,
        enrolled_time=datetime.utcnow(),
        progress=0.0,
        is_completed=False
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment

def update_chapter_progress(db: Session, student_id: int, chapter_id: int, is_completed: bool):
    progress = db.query(ChapterProgress).filter_by(student_id=student_id, chapter_id=chapter_id).first()
    if not progress:
        progress = ChapterProgress(
            student_id=student_id,
            chapter_id=chapter_id,
            is_completed=is_completed,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() if is_completed else None
        )
        db.add(progress)
    else:
        progress.is_completed = is_completed
        progress.end_time = datetime.utcnow() if is_completed else None
    db.commit()
    db.refresh(progress)
    return progress

def update_module_progress(db: Session, student_id: int, module_id: int, is_completed: bool):
    progress = db.query(ModuleProgress).filter_by(student_id=student_id, module_id=module_id).first()
    if not progress:
        progress = ModuleProgress(
            student_id=student_id,
            module_id=module_id,
            is_completed=is_completed,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() if is_completed else None
        )
        db.add(progress)
    else:
        progress.is_completed = is_completed
        progress.end_time = datetime.utcnow() if is_completed else None
    db.commit()
    db.refresh(progress)
    return progress

def update_stage_progress(db: Session, student_id: int, stage_id: int, is_completed: bool):
    progress = db.query(StageProgress).filter_by(student_id=student_id, stage_id=stage_id).first()
    if not progress:
        progress = StageProgress(
            student_id=student_id,
            stage_id=stage_id,
            is_completed=is_completed,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() if is_completed else None
        )
        db.add(progress)
    else:
        progress.is_completed = is_completed
        progress.end_time = datetime.utcnow() if is_completed else None
    db.commit()
    db.refresh(progress)
    return progress