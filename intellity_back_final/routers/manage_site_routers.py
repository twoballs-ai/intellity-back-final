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

from intellity_back_final.auth import role_checker
from intellity_back_final.fixtures_and_autocreates.role_init import initialize_roles_and_privileges
from intellity_back_final.models.course_editor_lms_models import Course, CourseCategory, Module, Stage as StageModel, Answer as AnswerModel, QuizLesson as QuizLessonModel
import logging

from intellity_back_final.models.course_study_lms_models import CourseEnrollment
from intellity_back_final.models.site_utils_models import LogType
from intellity_back_final.models.user_models import User
from intellity_back_final.routers.user import get_current_user
from intellity_back_final.utils.utils import log_action
from ..database import SessionLocal
from ..crud import teacher_lms_crud
from ..schemas import lms_schemas
from ..models.course_editor_lms_models import Chapter as ChapterModel, ClassicLesson, CourseModerationStatus, CourseStatus, QuizLesson, VideoLesson
import os
import shutil
from PIL import Image as PILImage

logger = logging.getLogger(__name__)

manage_site_views = APIRouter()


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
# @user_views.get("/siteuser/role-specific")
# async def read_siteuser_data(current_user: User = Depends(role_checker(["Administrator"]))):
#     print("fff")
#     return {"message": "Hello Admin!", "user": current_user.to_dict()}

@manage_site_views.post("/category/", response_model=lms_schemas.CourseCategory)
def create_course_category(
    category: lms_schemas.CourseCategoryCreate, 
    current_user: User = Depends(role_checker(["Administrator"])), 
    db: Session = Depends(get_db)
):
    db_category = teacher_lms_crud.get_category_by_title(db, title=category.title)
    if db_category:
        raise HTTPException(status_code=400, detail="категория уже существует")
    
    new_category = teacher_lms_crud.create_category(db=db, category=category, current_user=current_user)
    

    return new_category

#Эту функцию достаточно включать один раз что бы выполнить на начальном этапе.Этакая фикстура
# @manage_site_views.post("/initialize_roles_and_privileges/")
# def initialize_roles_and_privileges_endpoint(db: Session = Depends(get_db)):
#     try:
#         initialize_roles_and_privileges(db)
#         return {"status": "success", "message": "Roles and privileges initialized."}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))