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

from intellity_back_final.Minio import create_course_directory, upload_image
from intellity_back_final.auth import type_checker
from intellity_back_final.models.course_editor_lms_models import Course, CourseCategory, Module, Stage as StageModel, Answer as AnswerModel, QuizLesson as QuizLessonModel
import logging

from intellity_back_final.models.course_study_lms_models import CourseEnrollment
from intellity_back_final.models.user_models import User
from intellity_back_final.routers.user import get_current_user
from ..database import SessionLocal
from ..crud import teacher_lms_crud
from ..schemas import lms_schemas
from ..models.course_editor_lms_models import Chapter as ChapterModel, ClassicLesson, CourseModerationStatus, CourseStatus, QuizLesson, VideoLesson
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
def read_courses(course_id: int, current_user: User = Depends(get_current_user),  db: Session = Depends(get_db)):
    course = teacher_lms_crud.get_course_by_id(db, course_id=course_id)
    if not course:
        return JSONResponse(
            content={"status": False, "message": "Course not found"},
            status_code=404,
        )
    if course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not the owner of this course")
    
    chapters = db.query(ChapterModel).filter(ChapterModel.course_id == course_id).all()
    chapters_data = [
        {
            "id": chapter.id,
            "title": chapter.title,
            "description": chapter.description,
        }
        for chapter in chapters
    ]

    data = {
        "course": course.to_dict(),
        "chapters": chapters_data
    }

    return JSONResponse(
        content={"status": True, "data": data},
        status_code=200,
    )



@lms_views.post("/course/")
def create_course(
    title: str = Form(..., max_length=30),
    description: str = Form(None),
    category: int = Form(...),
    current_user: User = Depends(type_checker(["teacher_model"])),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Validate the file type
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG and PNG files are allowed.")

    # Verify the image
    try:
        with PILImage.open(file.file) as img:
            img.verify()
            file.file.seek(0)  # Reset file pointer to beginning after verification
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file.")

    # Check if the course already exists
    search_course = teacher_lms_crud.get_course_by_title(db, title=title)
    if search_course:
        raise HTTPException(status_code=400, detail="Course already exists")

    # Set default status_id if not provided
    default_status_id = 1

    # Create the course in the database
    course_create = teacher_lms_crud.create_course(
        db=db,
        course=lms_schemas.CourseCreate(title=title, description=description, category=category, status_id=default_status_id),
        user_id=current_user.id,
        cover_image_name=file.filename,

    )
    if not course_create:
        raise HTTPException(status_code=404, detail="Course not found")

    course_id = course_create.id

    # Create course directory structure in MinIO
    try:
        course_directory_name, covers_directory_name = create_course_directory(course_id, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Upload the cover image to MinIO
    try:
        file.file.seek(0)  # Ensure the file pointer is at the beginning
        file_data = file.file.read()
        cover_image_path = upload_image(
            file_name=file.filename,
            file_data=file_data,
            content_type=file.content_type,
            directory_name=covers_directory_name
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload cover image: {e}")

    # Update the course record with the cover image path
    course_create.cover_path = cover_image_path
    db.commit()
    db.refresh(course_create)

    return JSONResponse(
        content={
            "status": True,
            "data": course_create.to_dict(),
            "message": "You have successfully added the course."
        },
        status_code=200,
    )

@lms_views.put("/course/{course_id}")
def update_course(
    course_id: int,
    title: str = Form(..., max_length=30), 
    description: str = Form(None), 
    file: UploadFile = File(...),
    current_user: User = Depends(type_checker(["teacher_model"])),
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

    course = teacher_lms_crud.get_course_by_id(db, course_id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if the current user owns the course or has permission to edit it
    if course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this course")

    # Assume the directory for the course already exists
    covers_directory_name = f"{course_id}_{course.teacher_id}/covers/"

    # Upload the new cover image to MinIO
    file_data = file.file.read()
    image_url = upload_image(file.filename, file_data, file.content_type, covers_directory_name)

    # Update course fields
    course.title = title
    course.description = description
    course.cover_image_name = file.filename
    course.cover_path = image_url

    db.commit()
    db.refresh(course)

    return JSONResponse(
        content={
            "status": True,
            "data": course.to_dict(),
            "message": "Курс обновлен"
        },
        status_code=200,
    )

@lms_views.delete("/delete-course/{course_id}")
def delete_course(course_id: int, current_user: User = Depends(type_checker(["teacher_model"])), db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not the owner of this course")
    
    # Delete associated enrollments
    db.query(CourseEnrollment).filter(CourseEnrollment.course_id == course_id).delete()
    
    # Delete the course
    db.delete(course)
    db.commit()
    
    return JSONResponse(
        content={
            "status": True,
            "message": "Course deleted successfully."
        },
        status_code=200,
    )

@lms_views.delete("/archive-course/{course_id}")
def archive_course(course_id: int, current_user: User = Depends(type_checker(["teacher_model"])), db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not the owner of this course")
    
    # Find the "Archived" status ID
    archived_status = db.query(CourseStatus).filter(CourseStatus.status == "Архивный").first()
    
    if archived_status is None:
        raise HTTPException(status_code=500, detail="Archived status not found")

    # Change the status of the course to "Archived"
    course.status_id = archived_status.id
    db.commit()
    
    return JSONResponse(
        content={
            "status": True,
            "message": "Course archived successfully."
        },
        status_code=200,
    )


@lms_views.get("/course-chapter-list/{course_id}")
def read_chapter(course_id:int, db: Session = Depends(get_db)):
    
    chapter = teacher_lms_crud.get_course_chapters(db,course_id=course_id)

    return { "data": chapter}


@lms_views.get("/course-chapter-module-list/{chapter_id}")
def read_modules(chapter_id, db: Session = Depends(get_db)):
    
    chapter_modules = teacher_lms_crud.get_course_chapter_modules(db,chapter_id=chapter_id)

    return { "data": chapter_modules}

@lms_views.get("/module-stage-list/{module_id}")
def read_stages(module_id:int, db: Session = Depends(get_db)):
    try:

        module_stages = teacher_lms_crud.get_course_chapter_module_stages(db,module_id=module_id)
        
        return { "data": module_stages}

    except Exception as e:
        return JSONResponse(
            content={"status": False, "error": str(e)},
            status_code=500,
        )

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
async def add_chapter_to_course(
    data: lms_schemas.AddChapter, 
    current_user: User = Depends(type_checker(["teacher_model"])), 
    db: Session = Depends(get_db)
):
    try:
        # Получение курса
        course = db.query(Course).filter(Course.id == data.course_id).first()

        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        # Проверка прав доступа
        if course.teacher_id != current_user.id:
            raise HTTPException(status_code=403, detail="You are not the owner of this course")

        # Получение последней главы курса по полю sort_index
        last_chapter = db.query(ChapterModel).filter(ChapterModel.course_id == data.course_id).order_by(ChapterModel.sort_index.desc()).first()

        # Определение sort_index
        sort_index = last_chapter.sort_index + 1 if last_chapter else 1

        # Создание объекта главы и добавление в базу данных
        chapter_create = ChapterModel(
            course_id=data.course_id,
            title=data.title,
            description=data.description,
            sort_index=sort_index,
            is_exam=data.is_exam,
            exam_duration_minutes=data.exam_duration_minutes,
        )
        db.add(chapter_create)

        db.commit()
        db.refresh(chapter_create)  # Обновление объекта главы

        return JSONResponse(
            content={
                "status": True,
                "data": chapter_create.to_dict(),
                "message": "Chapter added"
            },
            status_code=200,
        )
    except Exception as e:
        return JSONResponse(
            content={"status": False, "error": str(e)},
            status_code=500,
        )

@lms_views.put("/update-chapter/{chapter_id}")
async def update_chapter(chapter_id: int, data: lms_schemas.UpdateChapter, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        # Получаем главу по ID
        chapter = db.query(ChapterModel).filter(ChapterModel.id == chapter_id).first()

        if not chapter:
            raise HTTPException(status_code=404, detail="Chapter not found")

        # Получаем курс через связанную главу
        course = db.query(Course).filter(Course.id == chapter.course_id).first()

        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        # Проверяем права доступа
        if course.teacher_id != current_user.id:
            raise HTTPException(status_code=403, detail="You are not the owner of this course")

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
                "data": chapter.to_dict(),
                "message":"Глава обновлена"
            },
            status_code=200,
        )
    except Exception as e:
        return JSONResponse(
            content={"status": False, "error": str(e)},
            status_code=500,
        )

class ChapterSortUpdate(BaseModel):
    id: int
    sort_index: int

@lms_views.put("/update_chapters_sort_indexes/{course_id}")
def update_chapters_sort_indexes(course_id: int, chapters: List[ChapterSortUpdate], db: Session = Depends(get_db)):
    # Получить ID глав, которые принадлежат курсу
    chapter_ids_in_course = db.query(ChapterModel.id).filter(ChapterModel.course_id == course_id).all()
    valid_ids = {id for (id,) in chapter_ids_in_course}
    
    # Проверить, что все переданные ID принадлежат к указанному курсу
    for chapter_update in chapters:
        if chapter_update.id not in valid_ids:
            raise HTTPException(status_code=404, detail=f"Chapter with id {chapter_update.id} does not belong to course {course_id}")

    # Обновить сортировочные индексы для каждой главы
    for chapter_update in chapters:
        chapter = db.query(ChapterModel).filter(ChapterModel.id == chapter_update.id).first()
        if chapter is None:
            raise HTTPException(status_code=404, detail=f"Chapter with id {chapter_update.id} not found")
        chapter.sort_index = chapter_update.sort_index
        db.add(chapter)
    
    # Сохранить изменения в базе данных
    db.commit()
    
    # Получить обновленный список глав
    updated_chapters = teacher_lms_crud.get_course_chapters(db, course_id=course_id)
    
    return JSONResponse(
        content={
            "status": True,
            "message": "Обновление сортировок прошло успешно.",
            "data": updated_chapters
        },
        status_code=200
    )

@lms_views.delete("/delete-chapter/")
async def delete_chapter(chapter_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        # Получаем главу по ID
        chapter_to_delete = db.query(ChapterModel).filter(ChapterModel.id == chapter_id).first()

        if not chapter_to_delete:
            raise HTTPException(status_code=404, detail="Chapter not found")

        # Получаем курс через связанную главу
        course = db.query(Course).filter(Course.id == chapter_to_delete.course_id).first()

        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        # Проверяем права доступа
        if course.teacher_id != current_user.id:
            raise HTTPException(status_code=403, detail="You are not the owner of this course")

        # Удаляем главу
        db.delete(chapter_to_delete)
        db.commit()  # Сохраняем изменения после удаления

        # Получаем все оставшиеся главы курса, отсортированные по sort_index
        remaining_chapters = db.query(ChapterModel).filter(
            ChapterModel.course_id == course.id
        ).order_by(ChapterModel.sort_index).all()

        # Пересчитываем и обновляем индексы оставшихся глав
        for new_index, chapter in enumerate(remaining_chapters):
            chapter.sort_index = new_index + 1  # Обновляем sort_index начиная с 1
            db.add(chapter)

        # Сохраняем изменения в базе данных
        db.commit()

        return JSONResponse(content={"status": True, "message": "Удаление главы произошло успешно."}, status_code=200)
    except Exception as e:
        return JSONResponse(
            content={"status": False, "error": str(e)},
            status_code=500,
        )



    
@lms_views.get("/module/")
def read_module(module_id:int, db: Session = Depends(get_db)):
    
    module = teacher_lms_crud.get_get_module_by_id(db,module_id=module_id)

    return { "data": module}

@lms_views.post("/add_module_to_chapter/")
def add_module_to_chapter(data: lms_schemas.AddModule, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        # Получаем главу по ID
        chapter = db.query(ChapterModel).filter(ChapterModel.id == data.chapter_id).first()

        if not chapter:
            raise HTTPException(status_code=404, detail="Chapter not found")

        # Получаем курс через связанную главу
        course = db.query(Course).filter(Course.id == chapter.course_id).first()

        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        # Проверяем права доступа
        if course.teacher_id != current_user.id:
            raise HTTPException(status_code=403, detail="You are not the owner of this course")

        # Получаем последний модуль в данной главе по полю sort_index
        last_module = db.query(Module).filter(Module.chapter_id == data.chapter_id).order_by(Module.sort_index.desc()).first()

        # Определяем sort_index
        sort_index = last_module.sort_index + 1 if last_module else 1

        # Добавляем новый модуль
        module_create = Module(
            chapter_id=data.chapter_id,
            title=data.title,
            sort_index=sort_index,
            description=data.description
        )
        db.add(module_create)

        # Сохраняем изменения в базе данных
        db.commit()
        db.refresh(module_create)  # Обновляем объект модуля после сохранения

        return JSONResponse(
            content={
                "status": True,
                "data": module_create.to_dict(),
                "message": "Module added successfully"
            },
            status_code=200,
        )
    except Exception as e:
        return JSONResponse(
            content={"status": False, "error": str(e)},
            status_code=500,
        )
    
@lms_views.put("/update-module/{module_id}")
async def update_module(module_id: int, data: lms_schemas.UpdateModule, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        # Получаем модуль по ID
        module = db.query(Module).filter(Module.id == module_id).first()
        if not module:
            raise HTTPException(status_code=404, detail="Module not found")

        # Получаем главу, к которой относится модуль
        chapter = db.query(ChapterModel).filter(ChapterModel.id == module.chapter_id).first()
        if not chapter:
            raise HTTPException(status_code=404, detail="Chapter not found")

        # Получаем курс, к которому относится глава
        course = db.query(Course).filter(Course.id == chapter.course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        # Проверяем права доступа
        if course.teacher_id != current_user.id:
            raise HTTPException(status_code=403, detail="You are not the owner of this course")

        # Обновляем поля модуля, если они переданы в запросе
        if data.title is not None:
            module.title = data.title
        if data.sort_index is not None:
            module.sort_index = data.sort_index
        if data.description is not None:
            module.description = data.description

        # Сохраняем изменения в базе данных
        db.commit()

        return JSONResponse(
            content={
                "status": True,
                "data": module.to_dict(),
                "message":"Вы успешно обновили модуль"
            },
            status_code=200,
        )
    except Exception as e:
        return JSONResponse(
            content={"status": False, "error": str(e)},
            status_code=500,
        )

class ModuleSortUpdate(BaseModel):
    id: int
    sort_index: int


@lms_views.put("/update_modules_sort_indexes/{chapter_id}")
def update_modules_sort_indexes(chapter_id: int, modules: List[ModuleSortUpdate], db: Session = Depends(get_db)):
    # Get the IDs of the modules that belong to the chapter
    module_ids_in_chapter = db.query(Module.id).filter(Module.chapter_id == chapter_id).all()
    valid_ids = {id for (id,) in module_ids_in_chapter}

    # Check that all provided IDs belong to the specified chapter
    for module_update in modules:
        if module_update.id not in valid_ids:
            raise HTTPException(status_code=404, detail=f"Module with id {module_update.id} does not belong to chapter {chapter_id}")

    # Update the sort indexes for each module
    for module_update in modules:
        module = db.query(Module).filter(Module.id == module_update.id).first()
        if module is None:
            raise HTTPException(status_code=404, detail=f"Module with id {module_update.id} not found")
        module.sort_index = module_update.sort_index
        db.add(module)

    # Commit changes to the database
    db.commit()

    # Get the updated list of modules
    updated_modules = db.query(Module).filter(Module.chapter_id == chapter_id).order_by(Module.sort_index).all()

    return JSONResponse(
        content={
            "status": True,
            "message": "Сортировка модулей обновлена успешно",
            "data": [module.to_dict() for module in updated_modules]
        },
        status_code=200
    )


@lms_views.patch("/patch-module/{module_id}")
async def patch_module(module_id: int, data: lms_schemas.PatchModule, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        # Получаем модуль по ID
        module = db.query(Module).filter(Module.id == module_id).first()
        if not module:
            raise HTTPException(status_code=404, detail="Module not found")

        # Получаем главу, к которой относится модуль
        chapter = db.query(ChapterModel).filter(ChapterModel.id == module.chapter_id).first()
        if not chapter:
            raise HTTPException(status_code=404, detail="Chapter not found")

        # Получаем курс, к которому относится глава
        course = db.query(Course).filter(Course.id == chapter.course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        # Проверяем права доступа
        if course.teacher_id != current_user.id:
            raise HTTPException(status_code=403, detail="You are not the owner of this course")

        # Обновляем поля модуля, если они переданы в запросе

        if data.sort_index is not None:
            module.sort_index = data.sort_index


        # Сохраняем изменения в базе данных
        db.commit()

        return JSONResponse(
            content={
                "status": True,
                "data": module.to_dict(),
                "message":"Вы успешно обновили модуль"
            },
            status_code=200,
        )
    except Exception as e:
        return JSONResponse(
            content={"status": False, "error": str(e)},
            status_code=500,
        )

@lms_views.delete("/delete-module/")
def delete_module(module_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        module = db.query(Module).filter(Module.id == module_id).first()
        if not module:
            raise HTTPException(status_code=404, detail="Module not found")

        # Get the chapter the module belongs to
        chapter = db.query(ChapterModel).filter(ChapterModel.id == module.chapter_id).first()
        if not chapter:
            raise HTTPException(status_code=404, detail="Chapter not found")

        # Get the course the chapter belongs to
        course = db.query(Course).filter(Course.id == chapter.course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        # Check access rights
        if course.teacher_id != current_user.id:
            raise HTTPException(status_code=403, detail="You are not the owner of this course")

        # Count the number of stages that will be deleted
        total_stages = db.query(StageModel).filter(StageModel.module_id == module_id).count()

        # Delete the module
        db.delete(module)
        db.commit()  # Commit the deletion before reordering

        # Get remaining modules in the chapter, sorted by sort_index
        remaining_modules = db.query(Module).filter(
            Module.chapter_id == chapter.id
        ).order_by(Module.sort_index).all()

        # Recalculate and update sort indexes of remaining modules
        for new_index, mod in enumerate(remaining_modules):
            mod.sort_index = new_index + 1  # Update sort_index starting from 1
            db.add(mod)

        # Save changes to the database
        db.commit()

        return JSONResponse(
            content={
                "status": True,
                "message": "Удаление модуля произошло успешно."
            },
            status_code=200,
        )
    except Exception as e:
        return JSONResponse(
            content={"status": False, "error": str(e)},
            status_code=500,
        )


@lms_views.put("/update/classic_lesson/")
async def update_classic_lesson(data: lms_schemas.ClassicLessonUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        # Получаем классический урок по ID
        classic_lesson = db.query(ClassicLesson).filter(ClassicLesson.id == data.stage_id).first()

        if not classic_lesson:
            raise HTTPException(status_code=404, detail="Classic lesson not found")

        # Получаем модуль, к которому относится урок
        module = db.query(Module).filter(Module.id == classic_lesson.module_id).first()
        if not module:
            raise HTTPException(status_code=404, detail="Module not found")

        # Получаем главу, к которой относится модуль
        chapter = db.query(ChapterModel).filter(ChapterModel.id == module.chapter_id).first()
        if not chapter:
            raise HTTPException(status_code=404, detail="Chapter not found")

        # Получаем курс, к которому относится глава
        course = db.query(Course).filter(Course.id == chapter.course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        # Проверяем права доступа
        if course.teacher_id != current_user.id:
            raise HTTPException(status_code=403, detail="You are not the owner of this course")
        classic_lesson = teacher_lms_crud.update_classic_lesson(db, data)
        return {"message": "Данные успешно обновлены", "data": classic_lesson}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@lms_views.put("/update/video_lesson/")
async def update_video_lesson(data: lms_schemas.VideoLessonUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        # Получаем видеоурок по ID
        video_lesson = db.query(VideoLesson).filter(VideoLesson.id == data.stage_id).first()

        if not video_lesson:
            raise HTTPException(status_code=404, detail="Video lesson not found")

        # Получаем модуль, к которому относится видеоурок
        module = db.query(Module).filter(Module.id == video_lesson.module_id).first()
        if not module:
            raise HTTPException(status_code=404, detail="Module not found")

        # Получаем главу, к которой относится модуль
        chapter = db.query(ChapterModel).filter(ChapterModel.id == module.chapter_id).first()
        if not chapter:
            raise HTTPException(status_code=404, detail="Chapter not found")

        # Получаем курс, к которому относится глава
        course = db.query(Course).filter(Course.id == chapter.course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        # Проверяем права доступа
        if course.teacher_id != current_user.id:
            raise HTTPException(status_code=403, detail="You are not the owner of this course")

        # Обновляем поля видеоурока, если они переданы в запросе
        video_lesson = teacher_lms_crud.update_video_lesson(db, data)
        return {"message": "Video lesson updated successfully", "data": video_lesson}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@lms_views.post("/add_stage_to_module/{lesson_type}/")
async def create_and_associate_lesson_route(
    lesson_type: str, 
    data: Union[lms_schemas.ClassicLesson, lms_schemas.VideoLesson, lms_schemas.QuizCreate], 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    try:
        # Проверка модуля, главы и курса
        module = db.query(Module).filter(Module.id == data.module_id).first()
        if not module:
            raise HTTPException(status_code=404, detail="Module not found")

        chapter = db.query(ChapterModel).filter(ChapterModel.id == module.chapter_id).first()
        if not chapter:
            raise HTTPException(status_code=404, detail="Chapter not found")

        course = db.query(Course).filter(Course.id == chapter.course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        if course.teacher_id != current_user.id:
            raise HTTPException(status_code=403, detail="You are not the owner of this course")

        # Вызов соответствующего метода на основе типа урока
        new_lesson, message = teacher_lms_crud.create_and_associate_lesson(db, lesson_type, data, module.id)

        return {"message": message, "data": new_lesson}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@lms_views.put("/update/quiz_lesson/")
async def update_quiz_route(data: lms_schemas.QuizUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        # Получаем тест по ID
        quiz = db.query(QuizLesson).filter(QuizLesson.id == data.stage_id).first()

        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")

        # Получаем модуль, к которому относится тест
        module = db.query(Module).filter(Module.id == quiz.module_id).first()
        if not module:
            raise HTTPException(status_code=404, detail="Module not found")

        # Получаем главу, к которой относится модуль
        chapter = db.query(ChapterModel).filter(ChapterModel.id == module.chapter_id).first()
        if not chapter:
            raise HTTPException(status_code=404, detail="Chapter not found")

        # Получаем курс, к которому относится глава
        course = db.query(Course).filter(Course.id == chapter.course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        # Проверяем права доступа
        if course.teacher_id != current_user.id:
            raise HTTPException(status_code=403, detail="You are not the owner of this course")

        # Обновляем поля теста, если они переданы в запросе
        updated_quiz = teacher_lms_crud.update_quiz(db=db, data=data)
        return {"message": "Quiz updated successfully", "data": updated_quiz}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@lms_views.delete("/delete-stage/{stage_id}")
async def delete_stage(stage_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        stage = db.query(StageModel).filter(StageModel.id == stage_id).first()

        if not stage:
            raise HTTPException(status_code=404, detail="Stage not found")

        module = db.query(Module).filter(Module.id == stage.module_id).first()
        if not module:
            raise HTTPException(status_code=404, detail="Module not found")

        chapter = db.query(ChapterModel).filter(ChapterModel.id == module.chapter_id).first()
        if not chapter:
            raise HTTPException(status_code=404, detail="Chapter not found")

        course = db.query(Course).filter(Course.id == chapter.course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        if course.teacher_id != current_user.id:
            raise HTTPException(status_code=403, detail="You are not the owner of this course")

        # Delete the stage
        db.delete(stage)
        db.commit()

        # Recalculate sort_index for remaining stages in the module
        remaining_stages = db.query(StageModel).filter(StageModel.module_id == module.id).order_by(StageModel.sort_index).all()
        for index, remaining_stage in enumerate(remaining_stages, start=1):
            remaining_stage.sort_index = index
        db.commit()

        return JSONResponse(content={"status": True, "message": "Stage deleted successfully."}, status_code=200)
    except Exception as e:
        return JSONResponse(
            content={"status": False, "message": str(e)},
            status_code=500,
        )


class StageSortUpdate(BaseModel):
    id: int
    sort_index: int

@lms_views.put("/update_stages_sort_indexes/{module_id}")
def update_stages_sort_indexes(module_id: int, stages: List[StageSortUpdate], db: Session = Depends(get_db)):
    # Get the IDs of the stages that belong to the module
    stage_ids_in_module = db.query(StageModel.id).filter(StageModel.module_id == module_id).all()
    valid_ids = {id for (id,) in stage_ids_in_module}

    # Check that all provided IDs belong to the specified module
    for stage_update in stages:
        if stage_update.id not in valid_ids:
            raise HTTPException(status_code=404, detail=f"Stage with id {stage_update.id} does not belong to module {module_id}")

    # Update the sort indexes for each stage
    for stage_update in stages:
        stage = db.query(StageModel).filter(StageModel.id == stage_update.id).first()
        if stage is None:
            raise HTTPException(status_code=404, detail=f"Stage with id {stage_update.id} not found")
        stage.sort_index = stage_update.sort_index
        db.add(stage)

    # Commit changes to the database
    db.commit()

    # Get the updated list of stages
    updated_stages = db.query(StageModel).filter(StageModel.module_id == module_id).order_by(StageModel.sort_index).all()

    return JSONResponse(
        content={
            "status": True,
            "message": "Сортировка этапов обновлена успешно",
            "data": [stage.to_dict() for stage in updated_stages]
        },
        status_code=200
    )

@lms_views.get("/stage/{stage_id}")
def read_stage(stage_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    course = (
        db.query(Course)
        .join(ChapterModel)
        .join(Module)
        .join(StageModel)
        .filter(StageModel.id == stage_id)
        .with_entities(Course.teacher_id)
        .first()
    )

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not the owner of this course")

    stage = db.query(StageModel).filter(StageModel.id == stage_id).first()
    if stage is None:
        raise HTTPException(status_code=404, detail="Stage not found")

    return stage.to_dict()

@lms_views.get("/teacher-courses/")
def get_teacher_courses(current_user: User = Depends(get_current_user),  skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Получение курсов для указанного преподавателя из базы данных, используя идентификатор пользователя

    courses = teacher_lms_crud.get_teacher_courses(db, teacher_id=current_user.id, skip=skip, limit=limit)
    courses_data = [course.to_dict() for course in courses]
    
    return JSONResponse(
        content={
            "status": True,
            "data": courses_data
        },
        status_code=200,
    )


@lms_views.put("/courses/{course_id}/send_for_moderation")
def send_course_for_moderation(course_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Ensure the user is authorized to update the course
    if course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this course")

    # Find the draft and awaiting moderation statuses
    draft_status = db.query(CourseStatus).filter_by(status='Черновик').first()
    awaiting_moderation_status = db.query(CourseModerationStatus).filter_by(status='Ожидает модерацию').first()

    if not draft_status or not awaiting_moderation_status:
        raise HTTPException(status_code=400, detail="Draft status or Awaiting Moderation status not found")

    # Update course statuses
    course.status_id = draft_status.id
    course.moderation_status_id = awaiting_moderation_status.id
    db.commit()

    return JSONResponse(
        content={
            "status": True,
            "message": "Курс отправлен на модерацию, это может занять некоторое время"
        },
        status_code=200,
    )
