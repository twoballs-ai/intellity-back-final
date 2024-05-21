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
from ..models.course_study_lms_models import CourseEnrollment, ChapterProgress, ModuleProgress, StageProgress

def are_all_lessons_completed(db: Session, student_id: int, module_id: int) -> bool:
    lessons = db.query(course_editor_lms_models.Stage).filter_by(module_id=module_id).all()
    for lesson in lessons:
        lesson_progress = db.query(StageProgress).filter_by(student_id=student_id, stage_id=lesson.id).first()
        if not lesson_progress or not lesson_progress.is_completed:
            return False
    return True

def are_all_modules_completed(db: Session, student_id: int, chapter_id: int) -> bool:
    modules = db.query(course_editor_lms_models.Module).filter_by(chapter_id=chapter_id).all()
    for module in modules:
        module_progress = db.query(ModuleProgress).filter_by(student_id=student_id, module_id=module.id).first()
        if not module_progress or not module_progress.is_completed:
            return False
    return True

def are_all_chapters_completed(db: Session, student_id: int, course_id: int) -> bool:
    chapters = db.query(course_editor_lms_models.Chapter).filter_by(course_id=course_id).all()
    for chapter in chapters:
        chapter_progress = db.query(ChapterProgress).filter_by(student_id=student_id, chapter_id=chapter.id).first()
        if not chapter_progress or not chapter_progress.is_completed:
            return False
    return True

def is_course_completed(db: Session, student_id: int, course_id: int) -> bool:
    chapters = db.query(course_editor_lms_models.Chapter).filter_by(course_id=course_id).all()
    for chapter in chapters:
        if not are_all_modules_completed(db, student_id, chapter.id):
            return False
        modules = db.query(course_editor_lms_models.Module).filter_by(chapter_id=chapter.id).all()
        for module in modules:
            if not are_all_lessons_completed(db, student_id, module.id):
                return False
    return True