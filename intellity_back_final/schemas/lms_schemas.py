from typing import List, Union

from pydantic import BaseModel
from typing import Optional

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
    teacher_id: int
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
 
 
class Stage(BaseModel):
    id: int
    module_id: int
    title: str
    items: Optional[dict] = None

    class Config:
        orm_mode = True
        
    
class StageItem(BaseModel):

    name: str
    descriptions: Optional[str] = None

 

class ClassicLesson(StageItem):
    html_code_text: str

class VideoLesson(StageItem):
    video_link: str

class ProgrammingLesson(StageItem):
    pass

class Question(BaseModel):
    question_text: str
    order: int
    is_true_answer: bool

class QuizLesson(StageItem):
    questions: List[Question]