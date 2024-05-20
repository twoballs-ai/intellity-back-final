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
from ..auth import  get_user_id_by_token
import json


from intellity_back_final.models.course_editor_lms_models import Course, CourseCategory, Module, Stage as StageModel, Question as QuestionModel, QuizLesson as QuizLessonModel

from ..database import SessionLocal
from ..crud import teacher_lms_crud
from ..schemas import lms_schemas
from ..models.course_editor_lms_models import Chapter as ChapterModel
lms_views = APIRouter()


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# pydantic:

# class SuggData(BaseModel):
#     # date: datetime
#     reason: int
#     author: str
#     receiver_depart: int
#     message: str
#     is_hidden: bool


class AddChapter(BaseModel):
    course_id: int
    title: str
    description: str
    
    
@lms_views.get("/category/")
def read_course_categories(skip: int = 0, limit: int = 100, to_select: bool = False, db: Session = Depends(get_db)):
    """_summary_

    Args:
        skip (int, optional): _description_. Defaults to 0.
        limit (int, optional): _description_. Defaults to 100.
        to_select (bool, optional): _description_. Defaults to False.
        db (Session, optional): _description_. Defaults to Depends(get_db).

    Returns:
        _type_: _description_
    """
    if to_select:
        categories = teacher_lms_crud.get_categoryes(db, skip=skip, limit=limit)
        categories_select = [category.to_select() for category in categories]
        
        return JSONResponse(
            content={
                "status": True,
                "data": categories_select,
            },
            status_code=200,
        )
    else:
        categories = teacher_lms_crud.get_categoryes(db, skip=skip, limit=limit)
        categories_data = [
            {
                "id": category.id,
                "title": category.title,
                "description": category.description,
                "total_courses": db.query(Course).filter(Course.category == category.id).count()
            }
            for category in categories
        ]

        return JSONResponse(
            content={
                "status": True,
                "data": categories_data,
            },
            status_code=200,
        )
@lms_views.post("/category/", response_model=lms_schemas.CourseCategory)
def create_course_category(category: lms_schemas.CourseCategoryCreate, db: Session = Depends(get_db)):
    db_category = teacher_lms_crud.get_category_by_title(db, title=category.title)
    if db_category:
        raise HTTPException(status_code=400, detail="категория уже существует")
    return teacher_lms_crud.create_category(db=db, category=category)


@lms_views.get("/courses/")
def read_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    
    courses = teacher_lms_crud.get_courses(db, skip=skip, limit=limit)
    
    # categories = [
    #     {
    #         "id": category.id,
    #         "title": category.title,
    #         "description": category.description,
    #         "count": db.query(Course).filter(Course.category == category.id).count()
    #     }
    #     for category in categories
    # ]

    # return JSONResponse(
    #     content={
    #         "status": True,
    #         "data": categories,
    #     },
    #     status_code=200,
    # )
    return courses



@lms_views.get("/course/")
def read_courses(course_id:int, db: Session = Depends(get_db)):
    
    course = teacher_lms_crud.get_get_course_by_id(db,course_id=course_id,)
    chapters=db.query().filter(ChapterModel.course_id == course_id).all()
    print(chapters)
    data=[]
    chapters = [
        {
            "id": category.id,
            "title": category.title,
            "description": category.description,

        }
        for category in chapters
    ]
    data.append(course_id)
    data.append(chapters)
    return JSONResponse(
        content={
            "status": True,
            "chapters": chapters,
        },
        status_code=200,
    )



@lms_views.post("/course/", response_model=lms_schemas.Course)
def create_course_category(course: lms_schemas.CourseCreate, user_id: int = Depends(get_user_id_by_token), db: Session = Depends(get_db)):
    db_course = teacher_lms_crud.get_course_by_title(db, title=course.title,)
    if db_course:
        raise HTTPException(status_code=400, detail="курс уже существует")
    return teacher_lms_crud.create_course(db=db, course=course, user_id=user_id)



@lms_views.get("/course-chapter-list/{course_id}")
def read_chapter(course_id, db: Session = Depends(get_db)):
    
    chapter = teacher_lms_crud.get_course_chapters(db,course_id=course_id)

    return { "data": chapter}


@lms_views.get("/course-chapter-module-list/{chapter_id}")
def read_modules(chapter_id, db: Session = Depends(get_db)):
    
    chapter_modules = teacher_lms_crud.get_course_chapter_modules(db,chapter_id=chapter_id)

    return { "data": chapter_modules}

@lms_views.get("/course-chapter-module-stage-list/{module_id}")
def read_stages(module_id, db: Session = Depends(get_db)):
    
    module_stages = teacher_lms_crud.get_course_chapter_module_stages(db,module_id=module_id)
    
    return { "data": module_stages}



@lms_views.get("/module/")
def read_module(module_id:int, db: Session = Depends(get_db)):
    
    module = teacher_lms_crud.get_get_module_by_id(db,module_id=module_id)

    return { "data": module}



@lms_views.post("/add_chapter_to_course/")
async def add_chapter_to_course(data: AddChapter, db: Session = Depends(get_db)):
    try:
        # Получаем количество глав для данного course_id
        chapter_count = db.query(func.count(ChapterModel.id)).filter(ChapterModel.course_id == data.course_id).scalar()

        # Создаем главу и устанавливаем sort_index
        chapter_create = ChapterModel(
            course_id=data.course_id,
            title=data.title,
            description=data.description,
            sort_index=chapter_count + 1  # Устанавливаем sort_index как количество глав плюс один
        )
        db.add(chapter_create)
        db.commit()

        return JSONResponse(
            content={
                "status": True,
                "chapters": chapter_create.to_dict(),
                "chapter_count": chapter_count + 1  # Возвращаем количество глав, увеличенное на один
            },
            status_code=200,
        )
    except Exception as e:
        return JSONResponse(
            content={"status": False, "error": str(e)},
            status_code=500,
        )
    
@lms_views.delete("/delete-chapter/")
def delete_chapter(chapter_id: int, db: Session = Depends(get_db)):
    chapter = db.query(ChapterModel).filter(ChapterModel.id == chapter_id).first()
    if chapter is None:
        raise HTTPException(status_code=404, detail="Chapter not found")
    db.delete(chapter)
    db.commit()
    return JSONResponse(
        content={
            "status": True,
            "text_for_budges":"Удаление раздела произошло успешно."
        },
        status_code=200,
    )

class AddModule(BaseModel):
    title: str
    description: str
    chapter_id:int
    
@lms_views.post("/add_module_to_chapter/")
def add_module_to_chapter(data:AddModule, db: Session = Depends(get_db)):
    module_create = Module(
            chapter_id=data.chapter_id,
            title=data.title,
            description=data.description
        )
    db.add(module_create)
    db.commit()
    return JSONResponse(
        content={
            "status": True,
            "modules": module_create.to_dict(),
        },
        status_code=200,
    )
    

@lms_views.delete("/delete-module/")
def delete_module(module_id: int, db: Session = Depends(get_db)):
    module = db.query(Module).filter(Module.id == module_id).first()
    if module is None:
        raise HTTPException(status_code=404, detail="Chapter not found")
    db.delete(module)
    db.commit()
    return JSONResponse(
        content={
            "status": True,
            "text_for_budges":"Удаление модуля произошло успешно."
        },
        status_code=200,
    )

# Маршрут для создания и привязки классического урока к стадии
@lms_views.post("/add_stage_to_module/classic_lesson/")
async def create_and_associate_classic_lesson_route(data:lms_schemas.ClassicLesson, db: Session = Depends(get_db)):
    # Создание и привязка классического урока к стадии
    try:
        new_classic_lesson = teacher_lms_crud.create_and_associate_classic_lesson(db, data)
        return {"message": "Classic lesson created and associated with stage successfully",
                "data":new_classic_lesson
                }
    except Exception as e:
        # Обработка возможных ошибок
        raise HTTPException(status_code=500, detail=str(e))
        
@lms_views.put("/update/classic_lesson/")
async def update_classic_lesson(data:lms_schemas.ClassicLessonUpdate, db: Session = Depends(get_db)):
    # Создание и привязка классического урока к стадии
    try:
        classic_lesson = teacher_lms_crud.update_classic_lesson(db, data)
        return {"message": "Classic lesson created and associated with stage successfully",
                "data":classic_lesson
                }
    except Exception as e:
        # Обработка возможных ошибок
        raise HTTPException(status_code=500, detail=str(e))

@lms_views.post("/add_stage_to_module/video_lesson/")
async def create_and_associate_video_lesson_route(data:lms_schemas.VideoLesson, db: Session = Depends(get_db)):
    # Создание и привязка классического урока к стадии
    try:
        new_video_lesson = teacher_lms_crud.create_and_associate_video_lesson(db, data)
        return {"message": "Video lesson created and associated with stage successfully",
                "data":new_video_lesson
                }
    except Exception as e:
        # Обработка возможных ошибок
        raise HTTPException(status_code=500, detail=str(e))

@lms_views.put("/update/video_lesson/")
async def update_video_lesson(data:lms_schemas.VideoLessonUpdate, db: Session = Depends(get_db)):
    # Создание и привязка классического урока к стадии
    try:
        video_lesson = teacher_lms_crud.update_video_lesson(db, data)
        return {"message": "Video lesson created and associated with stage successfully",
                "data":video_lesson
                }
    except Exception as e:
        # Обработка возможных ошибок
        raise HTTPException(status_code=500, detail=str(e))


@lms_views.post("/add_stage_to_module/quiz-lesson/")
def create_quiz_lesson(data: lms_schemas.QuizLessonCreate, db: Session = Depends(get_db)):
    # Создание нового урока типа "Quiz"
    
    try:
        new_quiz_lesson = teacher_lms_crud.create_and_associate_quiz_lesson(db, data)
        return {"message": "quiz lesson created and associated with stage successfully",
                "data":new_quiz_lesson
                }
    except Exception as e:
        # Обработка возможных ошибок
        raise HTTPException(status_code=500, detail=str(e))




@lms_views.delete("/delete-stage/")
def delete_stage(stage_id: int, db: Session = Depends(get_db)):
    module = db.query(StageModel).filter(StageModel.id == stage_id).first()
    if module is None:
        raise HTTPException(status_code=404, detail="Chapter not found")
    db.delete(module)
    db.commit()
    return JSONResponse(
        content={
            "status": True,
            "text_for_budges":"Удаление урока произошло успешно."
        },
        status_code=200,
    )


@lms_views.get("/stage/{stage_id}")
def read_stage(stage_id: int, db: Session = Depends(get_db)):
    # Пытаемся получить данные об этапе
    stage = teacher_lms_crud.get_stage(db, stage_id=stage_id)
    # Если этап не найден, вызываем исключение HTTP 404 Not Found
    if stage is None:
        raise HTTPException(status_code=404, detail="Stage not found")
    # Возвращаем данные об этапе в JSON-формате
    return stage.to_dict()


@lms_views.get("/teacher-courses/", response_model=List[lms_schemas.Course])
def get_teacher_courses(user_id: int = Depends(get_user_id_by_token), skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Получение курсов для указанного преподавателя из базы данных, используя идентификатор пользователя
    courses = teacher_lms_crud.get_teacher_courses(db, teacher_id=user_id, skip=skip, limit=limit)
    return courses