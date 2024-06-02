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

import json


from intellity_back_final.models.course_editor_lms_models import Course, CourseCategory, Module, Stage as StageModel, Answer as AnswerModel, QuizLesson as QuizLessonModel
import logging

from intellity_back_final.models.user_models import User
from intellity_back_final.routers.user import get_current_user
from ..database import SessionLocal
from ..crud import teacher_lms_crud
from ..schemas import lms_schemas
from ..models.course_editor_lms_models import Chapter as ChapterModel
import os
import shutil
from PIL import Image as PILImage

logger = logging.getLogger(__name__)

lms_views = APIRouter()


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

UPLOAD_DIRECTORY = "uploaded_directory"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)



    

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
def create_course_category(
    title: str = Form(..., max_length=30), 
    description: str = Form(None), 
    category: int = Form(...), 
    current_user: User = Depends(get_current_user), 
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG and PNG files are allowed.")

    # Verify the image
    try:
        with PILImage.open(file.file) as img:
            img.verify()
            file.file.seek(0)  # Reset file pointer to beginning after verify
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file.")

    search_course = teacher_lms_crud.get_course_by_title(db, title=title)
    if search_course:
        raise HTTPException(status_code=400, detail="Course already exists")

    course_create = teacher_lms_crud.create_course(
        db=db, 
        course=lms_schemas.CourseCreate(title=title, description=description, category=category), 
        user_id=current_user, 
        cover_image_name=file.filename, 
        cover_path=""
    )
    if not course_create:
        raise HTTPException(status_code=404, detail="Course not found")
    
    course_id = course_create.id
    course_title = course_create.title
    course_directory_name = f"{course_id}_{course_title.replace(' ', '_')}"
    course_directory_path = os.path.join(UPLOAD_DIRECTORY, course_directory_name)
    covers_directory_path = os.path.join(course_directory_path, "covers")
    media_directory_path = os.path.join(course_directory_path, "media")

    os.makedirs(covers_directory_path, exist_ok=True)
    os.makedirs(media_directory_path, exist_ok=True)

    file_location = os.path.join(covers_directory_path, file.filename)

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Update course with correct cover path
    course_create.cover_path = file_location
    db.commit()
    db.refresh(course_create)

    return course_create


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



@lms_views.get("/get_chapter/{chapter_id}")
async def get_chapter(chapter_id: int, db: Session = Depends(get_db)):
    try:
        # Получаем главу по ID
        chapter = db.query(ChapterModel).filter(ChapterModel.id == chapter_id).first()

        if not chapter:
            raise HTTPException(status_code=404, detail="Chapter not found")

        # Возвращаем главу в виде словаря
        return JSONResponse(
            content={
                "status": True,
                "chapter": chapter.to_dict(),
            },
            status_code=200,
        )
    except Exception as e:
        return JSONResponse(
            content={"status": False, "error": str(e)},
            status_code=500,
        )

@lms_views.post("/add_chapter_to_course/")
async def add_chapter_to_course(data: lms_schemas.AddChapter, db: Session = Depends(get_db)):
    try:
        # Получаем количество глав для данного course_id
        chapter_count = db.query(func.count(ChapterModel.id)).filter(ChapterModel.course_id == data.course_id).scalar()

        # Определяем sort_index
        sort_index = data.sort_index if data.sort_index is not None else chapter_count + 1

        # Создаем главу и устанавливаем все поля
        chapter_create = ChapterModel(
            course_id=data.course_id,
            title=data.title,
            description=data.description,
            sort_index=sort_index,
            is_exam=data.is_exam,
            exam_duration_minutes=data.exam_duration_minutes,
            previous_chapter_id=data.previous_chapter_id
        )
        db.add(chapter_create)
        db.commit()
        db.refresh(chapter_create)  # Обновляем объект для получения данных после коммита

        return JSONResponse(
            content={
                "status": True,
                "chapter": chapter_create.to_dict(),
                "chapter_count": chapter_count + 1  # Возвращаем количество глав, увеличенное на один
            },
            status_code=200,
        )
    except Exception as e:
        return JSONResponse(
            content={"status": False, "error": str(e)},
            status_code=500,
        )

@lms_views.put("/update-chapter/{chapter_id}")
async def update_chapter(chapter_id: int, data: lms_schemas.UpdateChapter, db: Session = Depends(get_db)):
    try:
        # Получаем главу по ID
        chapter = db.query(ChapterModel).filter(ChapterModel.id == chapter_id).first()

        if not chapter:
            raise HTTPException(status_code=404, detail="Chapter not found")

        # Обновляем поля главы, если они переданы в запросе
        if data.title is not None:
            chapter.title = data.title
        if data.description is not None:
            chapter.description = data.description
        if data.sort_index is not None:
            chapter.sort_index = data.sort_index
        if data.is_exam is not None:
            chapter.is_exam = data.is_exam
        if data.exam_duration_minutes is not None:
            chapter.exam_duration_minutes = data.exam_duration_minutes


        # Сохраняем изменения в базе данных
        db.commit()

        return JSONResponse(
            content={
                "status": True,
                "chapter": chapter.to_dict(),
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


    
@lms_views.get("/module/")
def read_module(module_id:int, db: Session = Depends(get_db)):
    
    module = teacher_lms_crud.get_get_module_by_id(db,module_id=module_id)

    return { "data": module}

@lms_views.post("/add_module_to_chapter/")
def add_module_to_chapter(data:lms_schemas.AddModule, db: Session = Depends(get_db)):
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
    
@lms_views.put("/update-module/{module_id}")
async def update_module(module_id: int, data: lms_schemas.UpdateModule, db: Session = Depends(get_db)):
    try:
        # Получаем модуль по ID
        module = db.query(Module).filter(Module.id == module_id).first()
        print(module)
        if not module:
            raise HTTPException(status_code=404, detail="Module not found")

        # Обновляем поля модуля, если они переданы в запросе
        if data.title is not None:
            module.title = data.title
        if data.description is not None:
            module.description = data.description

        # Сохраняем изменения в базе данных
        db.commit()

        return JSONResponse(
            content={
                "status": True,
                "data": module.to_dict(),
            },
            status_code=200,
        )
    except Exception as e:
        return JSONResponse(
            content={"status": False, "error": str(e)},
            status_code=500,
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

@lms_views.post("/add_stage_to_module/classic_lesson/")
async def create_and_associate_classic_lesson_route(data: lms_schemas.ClassicLesson, db: Session = Depends(get_db)):
    try:
        new_classic_lesson = teacher_lms_crud.create_and_associate_classic_lesson(db, data)
        return {"message": "Classic lesson created and associated with stage successfully", "data": new_classic_lesson}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@lms_views.put("/update/classic_lesson/")
async def update_classic_lesson(data: lms_schemas.ClassicLessonUpdate, db: Session = Depends(get_db)):
    try:
        classic_lesson = teacher_lms_crud.update_classic_lesson(db, data)
        return {"message": "Classic lesson updated successfully", "data": classic_lesson}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@lms_views.post("/add_stage_to_module/video_lesson/")
async def create_and_associate_video_lesson_route(data: lms_schemas.VideoLesson, db: Session = Depends(get_db)):
    try:
        new_video_lesson = teacher_lms_crud.create_and_associate_video_lesson(db, data)
        return {"message": "Video lesson created and associated with stage successfully", "data": new_video_lesson}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@lms_views.put("/update/video_lesson/")
async def update_video_lesson(data: lms_schemas.VideoLessonUpdate, db: Session = Depends(get_db)):
    try:
        video_lesson = teacher_lms_crud.update_video_lesson(db, data)
        return {"message": "Video lesson updated successfully", "data": video_lesson}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@lms_views.post("/add_stage_to_module/quiz_lesson/")
def create_quiz_route(quiz: lms_schemas.QuizCreate, db: Session = Depends(get_db)):
    try:
        new_quiz = teacher_lms_crud.create_quiz(db=db, quiz=quiz)
        return {"message": "Quiz created successfully", "data": new_quiz}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@lms_views.put("/update/quiz_lesson/")
def update_quiz_route(quiz_update: lms_schemas.QuizUpdate, db: Session = Depends(get_db)):
    try:
        updated_quiz = teacher_lms_crud.update_quiz(db=db, quiz_update=quiz_update)
        return {"message": "Quiz updated successfully", "data": updated_quiz}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@lms_views.delete("/delete-stage/{stage_id}")
def delete_stage(stage_id: int, db: Session = Depends(get_db)):
    stage = db.query(StageModel).filter(StageModel.id == stage_id).first()
    if stage is None:
        raise HTTPException(status_code=404, detail="Stage not found")
    db.delete(stage)
    db.commit()
    return JSONResponse(content={"status": True, "text_for_budges": "Stage deleted successfully."}, status_code=200)

@lms_views.get("/stage/{stage_id}")
def read_stage(stage_id: int, db: Session = Depends(get_db)):
    stage = db.query(StageModel).filter(StageModel.id == stage_id).first()
    if stage is None:
        raise HTTPException(status_code=404, detail="Stage not found")
    return stage.to_dict()


@lms_views.get("/teacher-courses/", response_model=List[lms_schemas.Course])
def get_teacher_courses(current_user: User = Depends(get_current_user),  skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Получение курсов для указанного преподавателя из базы данных, используя идентификатор пользователя

    courses = teacher_lms_crud.get_teacher_courses(db, teacher_id=current_user.id, skip=skip, limit=limit)
    return courses