from sqlalchemy import (Boolean
                        , Column
                        , Float
                        , ForeignKey
                        , Integer
                        , String
                        , BigInteger
                        , Text
                        , DateTime)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.orm import Session

from intellity_back_final.models.course_editor_lms_models import Chapter, Course, Module, Stage
from intellity_back_final.models.user_models import Student

# from intellity_back_final.models.course_editor_lms_models import Chapter, Course, Module, Stage
from ..database import Base

from typing import List
from typing import Optional

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class CourseEnrollment(Base):
    __tablename__ = "course_enrollment"
  
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("course_model.id"))
    student_id: Mapped[int] = mapped_column(ForeignKey("student_model.id"))
    enrolled_time: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), index=True)
    progress: Mapped[float] = mapped_column(Float, default=0.0)  # Процент прохождения курса
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    course: Mapped["Course"] = relationship("Course", back_populates="enrollments")
    student: Mapped["Student"] = relationship("Student", back_populates="enrollments")

    def __str__(self):
        return f"{self.student_id}-{self.course_id}"


class ChapterProgress(Base):
    __tablename__ = "chapter_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student_model.id"))
    chapter_id: Mapped[int] = mapped_column(ForeignKey("chapter_model.id"))
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    start_time: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    end_time: Mapped[DateTime] = mapped_column(DateTime, nullable=True)

    chapter: Mapped["Chapter"] = relationship("Chapter")
    student: Mapped["Student"] = relationship("Student")

    def __str__(self):
        return f"{self.student_id}-{self.chapter_id}"
    
    
class ModuleProgress(Base):
    __tablename__ = "module_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student_model.id"))
    module_id: Mapped[int] = mapped_column(ForeignKey("module_model.id"))
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    start_time: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    end_time: Mapped[DateTime] = mapped_column(DateTime, nullable=True)

    module: Mapped["Module"] = relationship("Module")
    student: Mapped["Student"] = relationship("Student")

    def __str__(self):
        return f"{self.student_id}-{self.module_id}"


class StageProgress(Base):
    __tablename__ = "stage_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student_model.id"))
    stage_id: Mapped[int] = mapped_column(ForeignKey("stage_model.id"))
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    start_time: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    end_time: Mapped[DateTime] = mapped_column(DateTime, nullable=True)

    stage: Mapped["Stage"] = relationship("Stage")
    student: Mapped["Student"] = relationship("Student")

    def __str__(self):
        return f"{self.student_id}-{self.stage_id}"