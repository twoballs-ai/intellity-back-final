from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException
from sqlalchemy import asc, create_engine
from sqlalchemy.orm import sessionmaker

from ..models import course_editor_lms_models
from ..schemas import lms_schemas
from typing import List



from sqlalchemy.orm import Session
from datetime import datetime
from ..models.course_study_lms_models import CourseEnrollment, ChapterProgress, ModuleProgress, StageProgress

def get_course_enrollment(db: Session, student_id: int, course_id: int):
    return db.query(CourseEnrollment).filter(
        CourseEnrollment.student_id == student_id,
        CourseEnrollment.course_id == course_id
    ).first()

def enroll_student_in_course(db: Session, student_id: int, course_id: int):
    # Создаем объект CourseEnrollment для записи подписки студента на курс
    enrollment = CourseEnrollment(
        student_id=student_id,
        course_id=course_id,
        enrolled_time=datetime.utcnow(),
        progress=0.0,
        is_completed=False
    )
    
    # Обновляем счетчик подписок для курса
    course = db.query(course_editor_lms_models.Course).filter(course_editor_lms_models.Course.id == course_id).first()
    if course:
        course.subscription_counter += 1
        db.add(enrollment)
        db.commit()
        db.refresh(enrollment)
        db.commit()
    else:
        # В случае, если курс не найден, выбрасываем исключение или выполняем другие действия
        raise HTTPException(status_code=404, detail="Course not found")
    
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
            status_id=1,
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

def get_stage_for_student(db: Session, stage_id: int):
    return db.query(course_editor_lms_models.Stage).filter(course_editor_lms_models.Stage.id == stage_id).first()

def get_course_chapter_module_stages(db: Session, module_id: int, user_id: int, skip: int = 0, limit: int = 100):
    module = db.query(course_editor_lms_models.Module).filter(course_editor_lms_models.Module.id == module_id).first()
    if module:
        stages = db.query(course_editor_lms_models.Stage).filter(course_editor_lms_models.Stage.module_id == module_id).order_by(asc(course_editor_lms_models.Stage.id)).all()
        stage_progress = db.query(StageProgress).filter(StageProgress.student_id == user_id).all()

        progress_map = {sp.stage_id: sp.is_completed for sp in stage_progress}

        list_items = []
        for stage in stages:
            if stage.type == 'quiz':
                stage_dict = stage.to_learn_dict()
            else:
                stage_dict = stage.to_dict()
            stage_dict['is_completed'] = progress_map.get(stage.id, False)
            list_items.append(stage_dict)

        return list_items