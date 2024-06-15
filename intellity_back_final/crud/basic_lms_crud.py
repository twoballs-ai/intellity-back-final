from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException
from sqlalchemy import asc, create_engine
from sqlalchemy.orm import sessionmaker

from ..models.course_editor_lms_models import Course, CourseStatus
from ..schemas import lms_schemas
from typing import List, Optional

from sqlalchemy.orm import Session
from datetime import datetime
from ..models.course_study_lms_models import CourseEnrollment, ChapterProgress, ModuleProgress, StageProgress

def get_recent_courses(db: Session, items: int = None):
    published_status = db.query(CourseStatus).filter(CourseStatus.status == "Опубликован").first()
    
    if not published_status:
        return []
    
    query = db.query(Course).filter(Course.status_id == published_status.id).order_by(Course.id.desc())
    
    if items:
        query = query.limit(items)
    
    return query.all()

def get_courses_by_cat(db: Session, skip: int = 0, limit: int = 100, category_id: Optional[int] = None):
    # Получаем объект статуса "Опубликован"
    published_status = db.query(CourseStatus).filter(CourseStatus.status == "Опубликован").first()
    
    # Если статус "Опубликован" не найден, возвращаем пустой список
    if not published_status:
        return []

    # Формируем запрос на получение курсов с указанной категорией и статусом "Опубликован"
    query = db.query(Course).filter(Course.status_id == published_status.id)
    if category_id:
        query = query.filter(Course.category == category_id)
    
    # Выполняем запрос с учётом пагинации и возвращаем результат
    return query.offset(skip).limit(limit).all()