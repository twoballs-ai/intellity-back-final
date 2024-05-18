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

def get_category(db: Session, category_id: int):
    return db.query(course_editor_lms_models.CourseCategory).filter(course_editor_lms_models.CourseCategory.id == category_id).first()


def get_category_by_title(db: Session, title: str):
    return db.query(course_editor_lms_models.CourseCategory).filter(course_editor_lms_models.CourseCategory.title == title).first()

def get_categoryes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(course_editor_lms_models.CourseCategory).offset(skip).limit(limit).all()


def create_category(db: Session, category: lms_schemas.CourseCategoryCreate):
    db_category = course_editor_lms_models.CourseCategory(title=category.title, description=category.description)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def get_courses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(course_editor_lms_models.Course).offset(skip).limit(limit).all()
    
def get_course_by_title(db: Session, title: str):
    return db.query(course_editor_lms_models.Course).filter(course_editor_lms_models.Course.title == title).first()   

def get_get_course_by_id(db: Session, course_id: int):
    return db.query(course_editor_lms_models.Course).filter_by(id = course_id).first()

def create_course(db: Session, course: lms_schemas.CourseCreate, user_id:int):
    db_course = course_editor_lms_models.Course(teacher_id=user_id, category=course.category, title=course.title, description=course.description)
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

def get_course_chapters(db: Session, course_id:int, skip: int = 0, limit: int = 100):
    chapters = db.query(course_editor_lms_models.Chapter).filter(course_editor_lms_models.Chapter.course_id == course_id).all()

    chapters_with_modules = []
    for chapter in chapters:
        modules = db.query(course_editor_lms_models.Module).filter(course_editor_lms_models.Module.chapter_id == chapter.id).all()
        
        chapter_data = {
            "id": chapter.id,
            "course_id": chapter.course_id,
            "title": chapter.title,
            "description": chapter.description,
            "modules": modules,
            "sort_index":chapter.sort_index,
        }
        chapters_with_modules.append(chapter_data)
    
    return chapters_with_modules

def get_course_chapter_modules(db: Session, chapter_id:int, skip: int = 0, limit: int = 100):
    
    chapter = db.query(course_editor_lms_models.Chapter).filter(course_editor_lms_models.Chapter.id == chapter_id).first()

    if chapter:
        modules = db.query(course_editor_lms_models.Module).filter(course_editor_lms_models.Module.chapter_id == chapter_id).all()
        return modules
    
def get_course_chapter_module_stages(db: Session, module_id:int, skip: int = 0, limit: int = 100):
    
    module = db.query(course_editor_lms_models.Module).filter(course_editor_lms_models.Module.id == module_id).first()
    # print(module)
    if module:
        stages = db.query(course_editor_lms_models.Stage).filter(course_editor_lms_models.Stage.module_id == module_id).order_by(asc(course_editor_lms_models.Stage.id)).all()

        list_tems=[]
        for items in stages:
            list_tems.append(items.to_dict())
        return list_tems

    
def get_get_chapter_by_id(db: Session, chapter_id: int):
    return db.query(course_editor_lms_models.Chapter).filter_by(id = chapter_id).first()

def get_get_module_by_id(db: Session, module_id: int):
    return db.query(course_editor_lms_models.Module).filter_by(id = module_id).first()



def create_and_associate_classic_lesson(db: Session,  data: lms_schemas.ClassicLesson) -> course_editor_lms_models.ClassicLesson:

    classic_lesson = course_editor_lms_models.ClassicLesson(module_id=data.module_id, title=data.title, html_code_text=data.html_code_text)
    db.add(classic_lesson)
    db.commit()
    db.refresh(classic_lesson)
    print(classic_lesson)
    
    return classic_lesson.to_dict()

def update_classic_lesson(db: Session, data: lms_schemas.ClassicLessonUpdate) -> dict:
    # Находим урок по его идентификатору
    classic_lesson = db.query(course_editor_lms_models.ClassicLesson).filter_by(id=data.stage_id).first()
    
    # Если урок не найден, можно выполнить соответствующие действия
    if not classic_lesson:
        return None  # Или какой-то другой возврат ошибки
    
    # Обновляем данные урока
    classic_lesson.title = data.title
    classic_lesson.html_code_text = data.html_code_text
    
    # Фиксируем изменения в базе данных
    db.commit()
    # Обновляем объект урока, чтобы он содержал актуальные данные из базы данных
    db.refresh(classic_lesson)
    
    # Возвращаем обновленный урок в виде словаря
    return classic_lesson.to_dict()

def create_and_associate_video_lesson(db: Session,  data: lms_schemas.VideoLesson) -> course_editor_lms_models.VideoLesson:

    video_lesson = course_editor_lms_models.VideoLesson(module_id=data.module_id, title=data.title, video_link=data.video_link)
    db.add(video_lesson)
    db.commit()
    db.refresh(video_lesson)
    print(video_lesson)
    
    return video_lesson.to_dict()
    
    
def update_video_lesson(db: Session, data: lms_schemas.VideoLessonUpdate) -> dict:
    # Находим урок по его идентификатору
    video_lesson = db.query(course_editor_lms_models.VideoLesson).filter_by(id=data.stage_id).first()
    
    # Если урок не найден, можно выполнить соответствующие действия
    if not video_lesson:
        return None  # Или какой-то другой возврат ошибки
    
    # Обновляем данные урока
    video_lesson.title = data.title
    video_lesson.video_link = data.video_link
    
    # Фиксируем изменения в базе данных
    db.commit()
    # Обновляем объект урока, чтобы он содержал актуальные данные из базы данных
    db.refresh(video_lesson)
    
    # Возвращаем обновленный урок в виде словаря
    return video_lesson.to_dict()

def create_and_associate_quiz_lesson(db: Session, stage_id: int, data: dict):
    print(data)

    # Проверяем, существует ли этап с указанным stage_id
    stage = db.query(course_editor_lms_models.Stage).filter(course_editor_lms_models.Stage.id == stage_id).first()
    if not stage:
        raise HTTPException(status_code=404, detail="Stage not found")

    # Создаем новый квиз
    quiz = course_editor_lms_models.QuizLesson(name=data.name, descriptions=data.descriptions, stage=stage)
    db.add(quiz)
    db.commit()

    # Создаем вопросы для квиза
    for question_data in data.questions:
        question = course_editor_lms_models.Question(question_text=question_data.question_text, 
                                        order=question_data.order, 
                                        is_true_answer=question_data.is_true_answer, 
                                        quiz=quiz)
        db.add(question)

    db.commit()
    return quiz


    
def get_stage(db: Session, stage_id: int):
    return db.query(course_editor_lms_models.Stage).filter(course_editor_lms_models.Stage.id == stage_id).first()


def get_teacher_courses(db: Session, teacher_id: int, skip: int = 0, limit: int = 100) -> List[course_editor_lms_models.Course]:
    # Query the database to retrieve courses for the specified teacher
    return db.query(course_editor_lms_models.Course).filter(course_editor_lms_models.Course.teacher_id == teacher_id).offset(skip).limit(limit).all()