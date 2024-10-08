from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException
from sqlalchemy import asc, create_engine
from sqlalchemy.orm import sessionmaker

from intellity_back_final.models.site_utils_models import LogType
from intellity_back_final.utils.utils import log_action

from ..models import course_editor_lms_models
from ..schemas import lms_schemas
from typing import List, Union


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


def create_category(db: Session, category: lms_schemas.CourseCategoryCreate,current_user):
    db_category = course_editor_lms_models.CourseCategory(title=category.title, description=category.description, )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    log_type = db.query(LogType).filter(LogType.name == "CREATE").first()
    if not log_type:
        raise HTTPException(status_code=500, detail="Log type 'CREATE' not found")
    # Log the action
    log_action(
        db=db,
        user_id=current_user.id,
        action=f"Created category: {category.title}",
        log_type_id=log_type.id,
        object_id=str(db_category.id),
        model_name="CourseCategory"  # Provide the model or table name
    )
    
    return db_category


def get_courses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(course_editor_lms_models.Course).offset(skip).limit(limit).all()
    
def get_course_by_title(db: Session, title: str):
    return db.query(course_editor_lms_models.Course).filter(course_editor_lms_models.Course.title == title).first()   

def get_course_by_id(db: Session, course_id: int):
    return db.query(course_editor_lms_models.Course).filter_by(id = course_id).first()

def create_course(db: Session, course: lms_schemas.CourseCreate, user_id: int, cover_image_name: str):
    db_course = course_editor_lms_models.Course(
        teacher_id=user_id,
        status_id=course.status_id,
        category=course.category,
        title=course.title,
        description=course.description,
        cover_image_name=cover_image_name,
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


def create_and_associate_lesson(
    db: Session, 
    lesson_type: str, 
    data: Union[lms_schemas.ClassicLesson, lms_schemas.VideoLesson, lms_schemas.QuizCreate], 
    module_id: int
):
    # Определяем sort_index
    last_stage = db.query(course_editor_lms_models.Stage).filter(course_editor_lms_models.Stage.module_id == module_id).order_by(course_editor_lms_models.Stage.sort_index.desc()).first()
    sort_index = last_stage.sort_index + 1 if last_stage else 1

    if lesson_type == "classic_lesson":
        lesson = course_editor_lms_models.ClassicLesson(module_id=module_id, title=data.title, html_code_text=data.html_code_text, sort_index=sort_index)
        message = "Вы успешно добавили классический урок"
    elif lesson_type == "video_lesson":
        lesson = course_editor_lms_models.VideoLesson(module_id=module_id, title=data.title, video_link=data.video_link, sort_index=sort_index)
        message = "Вы успешно добавили видео урок"
    elif lesson_type == "quiz_lesson":
        lesson = course_editor_lms_models.QuizLesson(module_id=module_id, title=data.title, sort_index=sort_index)
        message = "Вы успешно добавили квиз"
    else:
        raise HTTPException(status_code=400, detail="Invalid lesson type")
    
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson.to_dict(), message

def update_classic_lesson(db: Session, data: lms_schemas.ClassicLessonUpdate) -> dict:
    classic_lesson = db.query(course_editor_lms_models.ClassicLesson).filter_by(id=data.stage_id).first()
    if not classic_lesson:
        return None
    classic_lesson.title = data.title
    classic_lesson.html_code_text = data.html_code_text
    db.commit()
    db.refresh(classic_lesson)
    return classic_lesson.to_dict()

def update_video_lesson(db: Session, data: lms_schemas.VideoLessonUpdate) -> dict:
    video_lesson = db.query(course_editor_lms_models.VideoLesson).filter_by(id=data.stage_id).first()
    if not video_lesson:
        return None
    video_lesson.title = data.title
    video_lesson.video_link = data.video_link
    db.commit()
    db.refresh(video_lesson)
    return video_lesson.to_dict()


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