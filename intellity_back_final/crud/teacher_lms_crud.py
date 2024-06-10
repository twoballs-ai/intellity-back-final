from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException
from sqlalchemy import asc, create_engine
from sqlalchemy.orm import sessionmaker

from ..models import course_editor_lms_models
from ..schemas import lms_schemas
from typing import List


def get_category(db: Session, category_id: int):
    return db.query(course_editor_lms_models.CourseCategory).filter(course_editor_lms_models.CourseCategory.id == category_id).first()


def get_category_by_title(db: Session, title: str):
    return db.query(course_editor_lms_models.CourseCategory).filter(course_editor_lms_models.CourseCategory.title == title).first()

def get_categoryes(db: Session, skip: int = 0, limit: int = 100, to_select: bool = False):
    categories = db.query(course_editor_lms_models.CourseCategory).offset(skip).limit(limit).all()
    
    if to_select:
        return [category.to_select() for category in categories]
    
    return [
        {
            "id": category.id,
            "title": category.title,
            "description": category.description,
            "total_courses": db.query(course_editor_lms_models.Course).filter(course_editor_lms_models.Course.category == category.id).count()
        }
        for category in categories
    ]


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

def get_course_by_id(db: Session, course_id: int):
    return db.query(course_editor_lms_models.Course).filter_by(id = course_id).first()

def create_course(db: Session, course: lms_schemas.CourseCreate, user_id: int, cover_image_name: str, cover_path: str):
    db_course = course_editor_lms_models.Course(
        teacher_id=user_id,
        category=course.category,
        title=course.title,
        description=course.description,
        cover_image_name=cover_image_name,
        cover_path=cover_path
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

def get_course_chapters(db: Session, course_id: int, skip: int = 0, limit: int = 100):
    chapters = db.query(course_editor_lms_models.Chapter).filter(course_editor_lms_models.Chapter.course_id == course_id).all()

    chapters_with_modules = []
    for chapter in chapters:
        modules = db.query(course_editor_lms_models.Module).filter(course_editor_lms_models.Module.chapter_id == chapter.id).all()
        
        chapter_data = {
            "id": chapter.id,
            "course_id": chapter.course_id,
            "title": chapter.title,
            "description": chapter.description,
            "modules": [module.to_dict() for module in modules],
            "sort_index": chapter.sort_index,
            "is_exam": chapter.is_exam,
            "exam_duration": chapter.exam_duration_minutes,
            "previous_chapter_id": chapter.previous_chapter_id,
            "previous_chapter": chapter.previous_chapter.to_dict() if chapter.previous_chapter else None,
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



def create_and_associate_classic_lesson(db: Session, data: lms_schemas.ClassicLesson) -> course_editor_lms_models.ClassicLesson:
    classic_lesson = course_editor_lms_models.ClassicLesson(module_id=data.module_id, title=data.title, html_code_text=data.html_code_text)
    db.add(classic_lesson)
    db.commit()
    db.refresh(classic_lesson)
    return classic_lesson.to_dict()

def update_classic_lesson(db: Session, data: lms_schemas.ClassicLessonUpdate) -> dict:
    classic_lesson = db.query(course_editor_lms_models.ClassicLesson).filter_by(id=data.stage_id).first()
    if not classic_lesson:
        return None
    classic_lesson.title = data.title
    classic_lesson.html_code_text = data.html_code_text
    db.commit()
    db.refresh(classic_lesson)
    return classic_lesson.to_dict()


def create_and_associate_video_lesson(db: Session, data: lms_schemas.VideoLesson) -> course_editor_lms_models.VideoLesson:
    video_lesson = course_editor_lms_models.VideoLesson(module_id=data.module_id, title=data.title, video_link=data.video_link)
    db.add(video_lesson)
    db.commit()
    db.refresh(video_lesson)
    return video_lesson.to_dict()

def update_video_lesson(db: Session, data: lms_schemas.VideoLessonUpdate) -> dict:
    video_lesson = db.query(course_editor_lms_models.VideoLesson).filter_by(id=data.stage_id).first()
    if not video_lesson:
        return None
    video_lesson.title = data.title
    video_lesson.video_link = data.video_link
    db.commit()
    db.refresh(video_lesson)
    return video_lesson.to_dict()


def create_quiz(db: Session, quiz: lms_schemas.QuizCreate):
    db_quiz = course_editor_lms_models.QuizLesson(module_id=quiz.module_id, title=quiz.title)
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    return db_quiz.to_dict()


# def update_quiz(db: Session, quiz_update: lms_schemas.QuizUpdate):
#     # Получение quiz по его id
#     quiz = db.query(course_editor_lms_models.QuizLesson).filter(course_editor_lms_models.QuizLesson.id == quiz_update.quiz_id).first()
#     if not quiz:
#         raise HTTPException(status_code=404, detail="Quiz not found")

#     # Получение quiz_type_id на основе quiz_type
#     quiz_type = db.query(course_editor_lms_models.QuizType).filter(course_editor_lms_models.QuizType.name == quiz_update.quiz_type).first()
#     if not quiz_type:
#         raise HTTPException(status_code=404, detail="Quiz type not found")

#     # Обновление полей quiz
#     quiz.quiz_type_id = quiz_type.id
#     quiz.question = quiz_update.question

#     # Проверка на тип "radio" и количество правильных ответов
#     if quiz_type.name == "radio":
#         true_answers_count = sum(1 for q in quiz_update.answers if q.is_true_answer)
#         if true_answers_count > 1:
#             raise HTTPException(status_code=400, detail="For 'radio' type quiz, only one answer can be true")

#     # Удаление существующих ответов
#     db.query(course_editor_lms_models.Answer).filter(course_editor_lms_models.Answer.quiz_id == quiz.id).delete()

#     # Добавление новых ответов с порядком из frontend
#     for answer_data in quiz_update.answers:
#         answer = course_editor_lms_models.Answer(
#             quiz_id=quiz.id,
#             answer_text=answer_data.answer_text,
#             order=answer_data.order,
#             is_true_answer=answer_data.is_true_answer
#         )
#         db.add(answer)
    
#     db.commit()
#     db.refresh(quiz)
#     return quiz.to_dict()
def update_quiz(db: Session, data: lms_schemas.QuizUpdate):
    # Получение quiz по его id
    quiz_lesson = db.query(course_editor_lms_models.QuizLesson).filter_by(id=data.stage_id).first()


    if not quiz_lesson:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # Получение quiz_type_id на основе quiz_type
    quiz_type = db.query(course_editor_lms_models.QuizType).filter(course_editor_lms_models.QuizType.name == data.quiz_type).first()
    if not quiz_type:
        raise HTTPException(status_code=404, detail="Quiz type not found")

    # Обновление полей quiz
    if data.title:
        quiz_lesson.title = data.title

    quiz_lesson.quiz_type_id = quiz_type.id
    if data.question:
        quiz_lesson.question = data.question
    
    # Проверка на тип "radio" и количество правильных ответов
    if quiz_type.name == "radio":
        true_answers_count = sum(1 for q in data.answers if q.is_true_answer)
        if true_answers_count > 1:
            raise HTTPException(status_code=400, detail="For 'radio' type quiz, only one answer can be true")

    # Удаление существующих ответов
    db.query(course_editor_lms_models.Answer).filter(course_editor_lms_models.Answer.quiz_id == quiz_lesson.id).delete()

    # Добавление новых ответов с порядком из frontend
    for answer_data in data.answers:
        answer = course_editor_lms_models.Answer(
            quiz_id=quiz_lesson.id,
            answer_text=answer_data.answer_text,
            order=answer_data.order,
            is_true_answer=answer_data.is_true_answer
        )
        db.add(answer)
    
    db.commit()
    db.refresh(quiz_lesson)
    return quiz_lesson.to_dict()

def get_stage(db: Session, stage_id: int):
    return db.query(course_editor_lms_models.Stage).filter(course_editor_lms_models.Stage.id == stage_id).first()


def get_teacher_courses(db: Session, teacher_id: int, skip: int = 0, limit: int = 100) -> List[course_editor_lms_models.Course]:
    # Query the database to retrieve courses for the specified teacher
    return db.query(course_editor_lms_models.Course).filter(course_editor_lms_models.Course.teacher_id == teacher_id).offset(skip).limit(limit).all()