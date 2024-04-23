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
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session

import json


from intellity_back_final.models.lms_models import Course, CourseCategory, Module, Stage as StageModel, Question as QuestionModel, QuizLesson as QuizLessonModel

from ..database import SessionLocal
from ..crud import lms_crud
from ..schemas import lms_schemas
from ..models.lms_models import Chapter as ChapterModel
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
    
    
@lms_views.get("/category/", response_model=List[lms_schemas.CourseCategory])
def read_course_categoryies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    
    categories = lms_crud.get_categoryes(db, skip=skip, limit=limit)

    categories = [
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
            "data": categories,
        },
        status_code=200,
    )

@lms_views.post("/category/", response_model=lms_schemas.CourseCategory)
def create_course_category(category: lms_schemas.CourseCategoryCreate, db: Session = Depends(get_db)):
    db_category = lms_crud.get_category_by_title(db, title=category.title)
    if db_category:
        raise HTTPException(status_code=400, detail="категория уже существует")
    return lms_crud.create_category(db=db, category=category)


@lms_views.get("/courses/")
def read_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    
    courses = lms_crud.get_courses(db, skip=skip, limit=limit)
    
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
    
    course = lms_crud.get_get_course_by_id(db,course_id=course_id)
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
def create_course_category(course: lms_schemas.CourseCreate, db: Session = Depends(get_db)):
    db_course = lms_crud.get_course_by_title(db, title=course.title)
    if db_course:
        raise HTTPException(status_code=400, detail="курс уже существует")
    return lms_crud.create_course(db=db, course=course)

@lms_views.get("/course-chapter-list/{course_id}")
def read_chapter(course_id, db: Session = Depends(get_db)):
    
    chapter = lms_crud.get_course_chapters(db,course_id=course_id)

    return { "data": chapter}


@lms_views.get("/course-chapter-module-list/{chapter_id}")
def read_modules(chapter_id, db: Session = Depends(get_db)):
    
    chapter_modules = lms_crud.get_course_chapter_modules(db,chapter_id=chapter_id)

    return { "data": chapter_modules}

@lms_views.get("/course-chapter-module-stage-list/{module_id}")
def read_stages(module_id, db: Session = Depends(get_db)):
    
    module_stages = lms_crud.get_course_chapter_module_stages(db,module_id=module_id)
    
    return { "data": module_stages}



@lms_views.get("/module/")
def read_module(module_id:int, db: Session = Depends(get_db)):
    
    module = lms_crud.get_get_module_by_id(db,module_id=module_id)

    return { "data": module}



@lms_views.post("/add_chapter_to_course/")
async def add_chapter_to_course(data:AddChapter, db: Session = Depends(get_db)):
    # try:
    chapter_create = ChapterModel(
            course_id=data.course_id,
            title=data.title,
            description=data.description
        )
    db.add(chapter_create)
    db.commit()
    return JSONResponse(
        content={
            "status": True,
            "chapters": chapter_create.to_dict(),
        },
        status_code=200,
    )
    # except IntegrityError as e:
    #     db.rollback()
    #     return {"error": "An error occurred while adding the chapter. Please try again."}
    
    

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
    
class AddStage(BaseModel):
    title: str
    module_id:int
    
@lms_views.post("/add_stage_to_module/")
def add_stage_to_module(data:AddStage, db: Session = Depends(get_db)):
    stage_create = StageModel(
            module_id=data.module_id,
            title=data.title
        )
    db.add(stage_create)
    db.commit()
    return JSONResponse(
        content={
            "status": True,
            "modules": stage_create.to_dict(),
        },
        status_code=200,
    )
    
    


    
# Маршрут для создания и привязки классического урока к стадии
@lms_views.post("/stage/{stage_id}/classic_lesson/")
async def create_and_associate_classic_lesson_route(stage_id: int, data:lms_schemas.ClassicLesson, db: Session = Depends(get_db)):
    # Создание и привязка классического урока к стадии
    try:
        new_classic_lesson = lms_crud.create_and_associate_classic_lesson(db, stage_id, data)
        return {"message": "Classic lesson created and associated with stage successfully",
                "items":new_classic_lesson
                }
    except Exception as e:
        # Обработка возможных ошибок
        raise HTTPException(status_code=500, detail=str(e))
    

@lms_views.post("/stage/{stage_id}/video_lesson/")
async def create_and_associate_vdeo_lesson_route(stage_id: int, data:lms_schemas.VideoLesson, db: Session = Depends(get_db)):
    # Создание и привязка классического урока к стадии
    try:
        new_video_lesson = lms_crud.create_and_associate_video_lesson(db, stage_id, data)
        return {"message": "video lesson created and associated with stage successfully",
                "items":new_video_lesson
                }
    except Exception as e:
        # Обработка возможных ошибок
        raise HTTPException(status_code=500, detail=str(e))
        

@lms_views.post("/stage/{stage_id}/quiz_lesson/")
async def create_quiz(stage_id: int, data:lms_schemas.QuizLesson, db: Session = Depends(get_db)):
    try:
        new_quiz_lesson = lms_crud.create_and_associate_quiz_lesson(db, stage_id, data)
        return {"message": "quiz lesson created and associated with stage successfully",
                "items":new_quiz_lesson
                }
    except Exception as e:
        # Обработка возможных ошибок
        raise HTTPException(status_code=500, detail=str(e))


@lms_views.get("/stage/{stage_id}", response_model=lms_schemas.Stage)
def read_stage(stage_id: int, db: Session = Depends(get_db)):
    # Пытаемся получить данные об этапе
    stage = lms_crud.get_stage(db, stage_id=stage_id)
    # Если этап не найден, вызываем исключение HTTP 404 Not Found
    if stage is None:
        raise HTTPException(status_code=404, detail="Stage not found")
    # Возвращаем данные об этапе в JSON-формате
    return stage.to_dict()



