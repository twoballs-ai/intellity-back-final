from typing import List, Union
from pydantic import conlist, Field, field_validator
from pydantic import BaseModel,  validator
from typing import Optional

from enum import Enum

class CourseCategoryBase(BaseModel):
    title: str
    description: Union[str, None] = None

class CourseCategoryCreate(CourseCategoryBase):
    pass


class CourseCategory(CourseCategoryBase):
    id: int

    class Config:
        orm_mode = True

class CourseBase(BaseModel):
    category: int
    title: str
    description: Union[str, None] = None


class CourseCreate(CourseBase):
    pass


class Course(CourseBase):
    id: int

    class Config:
        orm_mode = True


class ChapterBase(BaseModel):
    category: int
    teacher_id: int
    title: str
    description: Union[str, None] = None
    technologicals: Union[str, None] = None

class ChapterCreate(ChapterBase):
    pass


class Chapter(ChapterBase):
    id: int

    class Config:
        orm_mode = True


class AddChapter(BaseModel):
    course_id: int
    title: str
    description: str
    sort_index: Optional[int] = None
    is_exam: Optional[bool] = False
    exam_duration_minutes: Optional[int] = None
    previous_chapter_id: Optional[int] = None


class UpdateChapter(BaseModel):
    title: Optional[str] = Field(None, max_length=30)
    description: Optional[str] = None
    sort_index: Optional[int] = None
    is_exam: Optional[bool] = None
    exam_duration_minutes: Optional[int] = None
    previous_chapter_id: Optional[int] = None


class AddModule(BaseModel):
    title: str
    description: str
    chapter_id:int


class UpdateModule(BaseModel):
    title: str
    description: str


class Stage(BaseModel):
    module_id: int
    title: str

    class Config:
        orm_mode = True

class ClassicLesson(Stage):
    html_code_text: str

    class Config:
        orm_mode = True

class ClassicLessonUpdate(BaseModel):
    stage_id: int
    title: str
    html_code_text: str

    class Config:
        orm_mode = True

class VideoLessonUpdate(BaseModel):
    stage_id: int
    title: str
    video_link: str

    class Config:
        orm_mode = True

class VideoLesson(Stage):
    video_link: str

    class Config:
        orm_mode = True

class ProgrammingLesson(Stage):
    code_string: str

    class Config:
        orm_mode = True

class QuizCreate(BaseModel):
    module_id: int
    title: str

class QuestionCreate(BaseModel):
    question_text: str
    order: int
    is_true_answer: bool