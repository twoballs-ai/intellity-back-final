from sqlalchemy.orm import Session
from datetime import datetime
from intellity_back_final.crud import student_lms_crud
from intellity_back_final.crud.student_lms_crud import enroll_student_in_course, get_course_enrollment, update_chapter_progress, update_module_progress, update_stage_progress
from intellity_back_final.models.course_study_lms_models import CourseEnrollment, ChapterProgress, ModuleProgress, StageProgress
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

from intellity_back_final.routers.user import get_current_user
import json


from intellity_back_final.models.course_editor_lms_models import Course as CourseModel, CourseCategory, Module, Stage as StageModel,  QuizLesson as QuizLessonModel, Chapter as ChapterModel

# from intellity_back_final.services import ExamService

from ..database import SessionLocal
from ..crud import teacher_lms_crud
from ..schemas import lms_schemas
from ..models.course_editor_lms_models import Answer, Chapter as ChapterModel, Course, QuizLesson
from intellity_back_final.models.user_models import Student, User
study_course_views = APIRouter()


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@study_course_views.get("/student/courses")
def get_enrolled_courses(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    enrollments = db.query(CourseEnrollment).filter(CourseEnrollment.student_id == current_user.id).all()
    if not enrollments:
        return JSONResponse(
        content={
            "status": False,
            "message": "вы не подписаны не на один курс",
            "data":[]
        },
        status_code=200,
    )

    courses = [enrollment.course_model.to_dict()  for enrollment in enrollments]
    return JSONResponse(
        content={
            "status": True,
            "data": courses,
        },
        status_code=200,
    )


@study_course_views.get("/check-enrollment/")
def check_enrollment(course_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    student_id = current_user.id  # Извлечение student_id из текущего пользователя
    enrollment = db.query(CourseEnrollment).filter_by(course_id=course_id, student_id=student_id).first()
    
    if enrollment:
        if enrollment.is_active:
            return JSONResponse(
                content={
                    "status": True,
                    "data": enrollment.to_dict(),
                    "enrolled_status": "enrolled"
                },
                status_code=200,
            )
        else:
            return JSONResponse(
                content={
                    "status": False,
                    "enrolled_status": "not enrolled"
                },
                status_code=200,
            )
    else:
        return JSONResponse(
            content={
                "status": False,
                "enrolled_status": "not enrolled"
            },
            status_code=200,
        )
@study_course_views.patch("/chapter_patch/{chapter_id}")
def update_chapter_progress(
    chapter_id: int, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db),
    update_locked: bool = Query(default=False, description="Update lock status")
):
    # Получаем главу по ID
    chapter = db.query(ChapterModel).filter_by(id=chapter_id).first()

    if chapter is None:
        raise HTTPException(status_code=404, detail="Chapter not found")

    # Получаем ID курса, к которому принадлежит глава
    course_id = chapter.course_id

    # Проверяем, подписан ли студент на курс
    course_enrollment = db.query(CourseEnrollment).filter(
        CourseEnrollment.course_id == course_id,
        CourseEnrollment.student_id == current_user.id
    ).first()

    if not course_enrollment:
        raise HTTPException(status_code=403, detail="You are not enrolled in this course")

    # Проверяем прогресс по главе или создаем новый, если его нет
    progress = db.query(ChapterProgress).filter_by(student_id=current_user.id, chapter_id=chapter_id).first()

    if progress:
        # Если прогресс есть, но start_time равен None, обновляем его
        if progress.start_time is None:
            progress.start_time = datetime.utcnow()

        # Если нужно обновить статус блокировки
        if update_locked:
            progress.is_locked = False

        db.commit()
        db.refresh(progress)

    # Возвращаем информацию о главе и прогрессе
    chapter_data = chapter.to_dict()
    chapter_data['progress'] = {
        'start_time': progress.start_time.isoformat() if progress.start_time else None,
        'is_completed': progress.is_completed,
        'is_locked': progress.is_locked,
        'end_time': progress.end_time.isoformat() if progress.end_time else None,
    }

    return JSONResponse(
        content={
            "status": True,
            "data": chapter_data,
        },
        status_code=200,
    )

    
@study_course_views.get("/learning-course-chapter-list/{course_id}")
def read_chapter(course_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    chapters = student_lms_crud.get_course_chapters(db, course_id=course_id)
    
    # Получаем прогресс по главам для текущего курса и студента
    chapter_progress = {cp.chapter_id: cp for cp in db.query(ChapterProgress).filter_by(student_id=current_user.id).all()}
    module_progress = {mp.module_id: mp for mp in current_user.module_progress}

    chapters_with_access = []

    for index, chapter in enumerate(chapters):
        chapter_data = chapter.to_dict()
        chapter_data['chapter_is_completed'] = False
        chapter_data['all_modules_completed'] = False
        chapter_data['exam_status'] = {}


        # Прогресс по текущей главе
        progress = chapter_progress.get(chapter.id)
        if progress:
            chapter_data['chapter_is_completed'] = progress.is_completed
            chapter_data['is_locked'] = progress.is_locked  # Берём статус блокировки из прогресса

        # Обработка экзаменов
        if chapter.is_exam:
            chapter_data['exam_status'] = {
                'exam_in_progress': progress and not progress.is_completed and progress.start_time is not None,
                'exam_start_time': progress.start_time.isoformat() if progress and progress.start_time else None,
                'exam_completed': progress.is_completed if progress else False
            }

        # Обработка модулей в главе
        chapter_data['modules'] = []
        for module in chapter.modules:
            module_data = module.to_dict()
            module_data['is_completed'] = False

            if module.id in module_progress:
                module_data['is_completed'] = module_progress[module.id].is_completed

            chapter_data['modules'].append(module_data)

        chapter_data['all_modules_completed'] = all(module['is_completed'] for module in chapter_data['modules'])

        chapters_with_access.append(chapter_data)

    return {"data": chapters_with_access}


@study_course_views.get("/module-stage-list/{module_id}")
def read_stages(module_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        module = db.query(Module).filter(Module.id == module_id).first()
        
        if module is None:
            raise HTTPException(status_code=404, detail="Module not found")
        
        # Retrieve the course ID
        course_id = module.chapter.course_id
        
        # Verify if the student is enrolled in the course corresponding to the module
        course_enrollment = db.query(CourseEnrollment).filter(
            CourseEnrollment.course_id == course_id,
            CourseEnrollment.student_id == current_user.id
        ).first()
        
        if not course_enrollment:
            raise HTTPException(status_code=403, detail="You are not enrolled in this course")
        
        # Check if progress exists
        progress = db.query(ModuleProgress).filter_by(student_id=current_user.id, module_id=module_id).first()
        if progress:
            # If start_time is empty or null, set it to the current time
            if progress.start_time is None:
                progress.start_time = datetime.utcnow()
                db.commit()
                db.refresh(progress)
        
        # Retrieve the module stages
        module_stages = student_lms_crud.get_course_chapter_module_stages(db, module_id=module_id, user_id=current_user.id)
            
        return {"data": module_stages}

    except Exception as e:
        return JSONResponse(
            content={"status": False, "error": str(e)},
            status_code=500,
        )
        
@study_course_views.post("/enroll/{course_id}")
def enroll_student(course_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    student = db.query(Student).get(current_user.id)
    course = db.query(CourseModel).get(course_id)
    
    if not student or not course:
        raise HTTPException(status_code=404, detail="Student or Course not found")
    
    enrollment = get_course_enrollment(db, student.id, course_id)
    
    if enrollment:
        if enrollment.is_active:
            return JSONResponse(
                content={
                    "status": False,
                    "data": "Student is already enrolled in this course",
                    "enrolled_status": "enrolled"
                },
                status_code=400,
            )
        else:
            # Если студент уже зарегистрирован, но запись не активна
            course.subscription_counter += 1
            enrollment.is_active = True
            db.commit()
            return JSONResponse(
                content={
                    "status": True,
                    "data": enrollment.to_dict(),
                    "message": "Вы снова подписались на курс",
                    "enrolled_status": "enrolled"
                },
                status_code=200,
            )
    
    enroll = enroll_student_in_course(db, student.id, course_id)
    return JSONResponse(
        content={
            "status": True,
            "data": enroll.to_dict(),
            "message": "Вы успешно подписались на курс",
            "enrolled_status": "enrolled"
        },
        status_code=200,
    )




@study_course_views.delete("/unsubscribe/{course_id}")
def unsubscribe_student(course_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    student = db.query(Student).get(current_user.id)
    course = db.query(Course).get(course_id)
    
    if not student or not course:
        raise HTTPException(status_code=404, detail="Student or Course not found")
    
    enrollment = db.query(CourseEnrollment).filter_by(student_id=student.id, course_id=course_id).first()
    
    if not enrollment:
        raise HTTPException(status_code=400, detail="Student is not enrolled in this course")
    
    # Delete all associated progress
    db.query(ChapterProgress).filter_by(student_id=student.id, chapter_id=enrollment.course_id).delete()
    db.query(ModuleProgress).filter_by(student_id=student.id, module_id=enrollment.course_id).delete()
    db.query(StageProgress).filter_by(student_id=student.id, stage_id=enrollment.course_id).delete()
    
    # Delete enrollment
    db.delete(enrollment)
    
    # Decrement subscription counter
    if enrollment.is_active == True:
        course.subscription_counter -= 1
    
    db.commit()

    return JSONResponse(
        content={
            "status": True,
            "message": "Вы успешно отписались от курса и весь ваш прогресс был удален.",
            "enrolled_status": "unenrolled"
        },
        status_code=200,
    )


@study_course_views.patch("/unenroll/light/{course_id}")
def unenroll_student_light(course_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    student = db.query(Student).get(current_user.id)
    course = db.query(CourseModel).get(course_id)

    if not student or not course:
        raise HTTPException(status_code=404, detail="Student or Course not found")

    enrollment = db.query(CourseEnrollment).filter_by(student_id=student.id, course_id=course_id).first()
    if not enrollment:
        raise HTTPException(status_code=400, detail="Student is not enrolled in this course")

    # Set enrollment to inactive
    enrollment.is_active = False

    # Decrease subscription counter
    course.subscription_counter -= 1

    db.commit()
    
    return JSONResponse(
        content={
            "status": True,
            "message": "You have successfully unenrolled from the course."
        },
        status_code=200,
    )

@study_course_views.post("/update_chapter/{chapter_id}")
def update_chapter(student_id: int, chapter_id: int, is_completed: bool, db: Session = Depends(get_db)):
    return update_chapter_progress(db, student_id, chapter_id, is_completed)

@study_course_views.post("/update_module/{module_id}")
def update_module(student_id: int, module_id: int, is_completed: bool, db: Session = Depends(get_db)):
    return update_module_progress(db, student_id, module_id, is_completed)

@study_course_views.post("/update_stage_progress/{stage_id}/")
def update_stage(stage_id: int, is_completed: bool, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Verify the user's enrollment in the course
    stage = student_lms_crud.get_stage_for_student(db, stage_id=stage_id)
    
    if stage is None:
        raise HTTPException(status_code=404, detail="Stage not found")
    
    # Retrieve the course ID
    course_id = None
    if stage.module:
        course_id = stage.module.chapter.course_id
    # Verify if the student is enrolled in the course corresponding to the stage
    course_enrollment = db.query(CourseEnrollment).filter(
        CourseEnrollment.course_id == course_id,
        CourseEnrollment.student_id == current_user.id
    ).first()
    
    if not course_enrollment:
        raise HTTPException(status_code=403, detail="You are not enrolled in this course")
    update = update_stage_progress(db, current_user.id, stage_id, is_completed)
    return JSONResponse(
        content={
            "status": True,
            "data": update.to_dict(),
        },
        status_code=200,
    )

@study_course_views.get("/stage/{stage_id}")
def read_stage(stage_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Retrieve the stage
    stage = student_lms_crud.get_stage_for_student(db, stage_id=stage_id)
    
    if stage is None:
        raise HTTPException(status_code=404, detail="Stage not found")
    
    # Retrieve the course ID
    course_id = None
    if stage.module:
        course_id = stage.module.chapter.course_id
    
    # Verify if the student is enrolled in the course corresponding to the stage
    course_enrollment = db.query(CourseEnrollment).filter(
        CourseEnrollment.course_id == course_id,
        CourseEnrollment.student_id == current_user.id
    ).first()
    
    if not course_enrollment:
        raise HTTPException(status_code=403, detail="You are not enrolled in this course")
    
    # Check the stage progress or create if it doesn't exist
    progress = db.query(StageProgress).filter_by(student_id=current_user.id, stage_id=stage_id).first()

    if progress:

        if progress.start_time is None:
            # If progress exists but start_time is None, update it
            progress.start_time = datetime.utcnow()
            db.commit()
            db.refresh(progress)
    
    # Format the data based on the stage type
    if isinstance(stage, QuizLesson):
        stage_data = stage.to_learn_dict()
    else:
        stage_data = stage.to_dict()
    
    # Return the formatted data as a JSON response
    return JSONResponse(
        content={
            "status": True,
            "data": stage_data,
        },
        status_code=200,
    )

@study_course_views.post("/check_quiz_answers/{stage_id}")
def check_quiz_answers(stage_id: int, answers: List[int], db: Session = Depends(get_db)):
    # Get the stage (quiz lesson) from the database
    quiz_lesson = db.query(QuizLesson).filter(QuizLesson.id == stage_id).first()
    if not quiz_lesson:
        raise HTTPException(status_code=404, detail="Quiz lesson not found")
    
    # Get the correct answers for the quiz lesson from the database
    correct_answers = db.query(Answer).filter(Answer.quiz_id == stage_id, Answer.is_true_answer == True).all()
    correct_answer_ids = set(answer.id for answer in correct_answers)
    
    # Check if the provided answers match the correct answers
    provided_answer_ids = set(answers)
    if provided_answer_ids == correct_answer_ids:
            # Return the formatted data as a JSON response
        return JSONResponse(
            content={
                "status": True,
                "message": "All answers are correct!"
            },
            status_code=200,
        )
    else:
        return JSONResponse(
            content={
                "status": False,
                "message": "Some answers are incorrect."
            },
            status_code=200,
        )



@study_course_views.post("/start_exam/{chapter_id}")
def update_chapter_progress(
    chapter_id: int, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db),
):
    # Получаем главу по ID
    chapter = db.query(ChapterModel).filter_by(id=chapter_id).first()

    if chapter is None:
        raise HTTPException(status_code=404, detail="Chapter not found")

    # Получаем ID курса, к которому принадлежит глава
    course_id = chapter.course_id

    # Проверяем, подписан ли студент на курс
    course_enrollment = db.query(CourseEnrollment).filter(
        CourseEnrollment.course_id == course_id,
        CourseEnrollment.student_id == current_user.id
    ).first()

    if not course_enrollment:
        raise HTTPException(status_code=403, detail="You are not enrolled in this course")

    # Проверяем прогресс по главе или создаем новый, если его нет
    progress = db.query(ChapterProgress).filter_by(student_id=current_user.id, chapter_id=chapter_id).first()

    if progress:
        # Если прогресс есть, но start_time равен None, обновляем его
        if progress.start_time is None:
            progress.start_time = datetime.utcnow()

        # Если нужно обновить статус блокировки
        if progress.is_locked is True:
            progress.is_locked = False

        db.commit()
        db.refresh(progress)

    # Возвращаем информацию о главе и прогрессе
    chapter_data = chapter.to_dict()
    chapter_data['progress'] = {
        'start_time': progress.start_time.isoformat() if progress.start_time else None,
        'is_completed': progress.is_completed,
        'is_locked': progress.is_locked,
        'end_time': progress.end_time.isoformat() if progress.end_time else None,
    }

    return JSONResponse(
        content={
            "status": True,
            "data": chapter_data,
        },
        status_code=200,
    )
# @study_course_views.post("/submit_exam/{chapter_id}")
# def submit_exam(chapter_id: int, answers: List[schemas.Answer], db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
#     return ExamService.submit_exam(chapter_id, current_user.id, answers, db)

# @study_course_views.post("/complete_exam/{chapter_id}")
# def complete_exam(chapter_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     return ExamService.complete_exam(chapter_id, current_user.id, db)
