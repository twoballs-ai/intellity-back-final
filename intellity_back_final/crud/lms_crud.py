from sqlalchemy.orm import Session

from ..models import lms_models
from ..schemas import lms_schemas


# def get_user(db: Session, user_id: int):
#     return db.query(models.User).filter(models.User.id == user_id).first()


# def get_user_by_email(db: Session, email: str):
#     return db.query(models.User).filter(models.User.email == email).first()

def get_category(db: Session, category_id: int):
    return db.query(lms_models.CourseCategory).filter(lms_models.CourseCategory.id == category_id).first()


def get_category_by_title(db: Session, title: str):
    return db.query(lms_models.CourseCategory).filter(lms_models.CourseCategory.title == title).first()

def get_categoryes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(lms_models.CourseCategory).offset(skip).limit(limit).all()


def create_category(db: Session, category: lms_schemas.CourseCategoryCreate):
    db_category = lms_models.CourseCategory(title=category.title, description=category.description)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def get_courses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(lms_models.Course).offset(skip).limit(limit).all()
    
def get_course_by_title(db: Session, title: str):
    return db.query(lms_models.Course).filter(lms_models.Course.title == title).first()   

def get_get_course_by_id(db: Session, course_id: int):
    return db.query(lms_models.Course).filter_by(id = course_id).first()

def create_course(db: Session, course: lms_schemas.CourseCreate):
    db_course = lms_models.Course(teacher_id=course.teacher_id, category=course.category, title=course.title, description=course.description)
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

def get_course_chapters(db: Session, course_id:int, skip: int = 0, limit: int = 100):
    chapters = db.query(lms_models.Chapter).filter(lms_models.Chapter.course_id == course_id).all()

    chapters_with_modules = []
    for chapter in chapters:
        modules = db.query(lms_models.Module).filter(lms_models.Module.chapter_id == chapter.id).all()
        
        chapter_data = {
            "id": chapter.id,
            "course_id": chapter.course_id,
            "title": chapter.title,
            "description": chapter.description,
            "modules": modules
        }
        chapters_with_modules.append(chapter_data)
    
    return chapters_with_modules

def get_course_chapter_modules(db: Session, chapter_id:int, skip: int = 0, limit: int = 100):
    
    chapter = db.query(lms_models.Chapter).filter(lms_models.Chapter.id == chapter_id).first()

    if chapter:
        modules = db.query(lms_models.Module).filter(lms_models.Module.chapter_id == chapter_id).all()
        return modules
    
def get_course_chapter_module_stages(db: Session, module_id:int, skip: int = 0, limit: int = 100):
    
    module = db.query(lms_models.Module).filter(lms_models.Module.id == module_id).first()
    # print(module)
    if module:
        stages = db.query(lms_models.Stage).filter(lms_models.Stage.module_id == module_id).all()
        list_tems=[]
        for items in stages:
            list_tems.append(items.to_dict())
        return list_tems

    
def get_get_chapter_by_id(db: Session, chapter_id: int):
    return db.query(lms_models.Chapter).filter_by(id = chapter_id).first()

def get_get_module_by_id(db: Session, module_id: int):
    return db.query(lms_models.Module).filter_by(id = module_id).first()


def create_and_associate_classic_lesson(db: Session, stage_id: int, text: str) -> None:
    # Создаем экземпляр класса ClassicLesson с переданным текстом
    classic_lesson = lms_models.ClassicLesson(text=text)
    
    # Получаем стадию (stage) по ее ID
    stage = db.query(lms_models.Stage).filter(lms_models.Stage.id == stage_id).first()
    
    # Если стадия с указанным ID существует, привязываем к ней classic_lesson
    if stage:
        # Создаем экземпляр класса StageItem для "classic lesson" и привязываем его к стадии
        classic_lesson_item = lms_models.ClassicLesson(text=text, stage=stage)
        db.add(classic_lesson_item)
        db.commit()
        db.refresh(classic_lesson_item)
    else:
        # Если стадия не найдена, вы можете обработать это согласно вашим требованиям
        pass
    
def get_stage(db: Session, stage_id: int):
    return db.query(lms_models.Stage).filter(lms_models.Stage.id == stage_id).first()