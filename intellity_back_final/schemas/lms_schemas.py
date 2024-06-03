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
        from_attributes = True

class CourseBase(BaseModel):
    title: str = Field(..., max_length=30)
    description: Optional[str]
    category: int

class CourseCreate(CourseBase):
    pass

class Course(CourseBase):
    id: int
    course_views_counter: int
    subscription_counter: int
    cover_image_name: Optional[str] = None
    cover_path: Optional[str] = None

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
        from_attributes = True


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
        from_attributes = True

class ClassicLesson(Stage):
    html_code_text: str

    class Config:
        from_attributes = True

class ClassicLessonUpdate(BaseModel):
    stage_id: int
    title: str
    html_code_text: str

    class Config:
        from_attributes = True

class VideoLessonUpdate(BaseModel):
    stage_id: int
    title: str
    video_link: str

    class Config:
        from_attributes = True

class VideoLesson(Stage):
    video_link: str

    class Config:
        from_attributes = True

class ProgrammingLesson(Stage):
    code_string: str

    class Config:
        from_attributes = True

class QuizCreate(BaseModel):
    module_id: int
    title: str

class AnswerCreate(BaseModel):
    answer_text: str
    is_true_answer: bool
    order: int

class QuizUpdate(BaseModel):
    stage_id: int
    title: str
    quiz_type: str
    question: str
    answers: List[AnswerCreate]

    class Config:
        from_attributes = True