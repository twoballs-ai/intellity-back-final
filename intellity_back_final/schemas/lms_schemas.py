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
        
        
class StageItemBase(BaseModel):
    type: str

class ClassicLessonBase(StageItemBase):
    text: Optional[str]

class StageItem(StageItemBase):
    id: int
    stage_id: int

    class Config:
        orm_mode = True

class ClassicLesson(StageItem):
    text: str

class StageBase(BaseModel):
    title: str

class StageCreate(StageBase):
    module_id: int

class Stage(StageBase):
    id: int
    module_id: int
    items: Optional[Union[ClassicLesson, StageItem]] = None

    class Config:
        orm_mode = True