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
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    course_model: Mapped["Course"] = relationship("Course", back_populates="enrollments_model")
    student_model: Mapped["Student"] = relationship("Student", back_populates="enrollments_model")

    def __str__(self):
        return f"{self.student_id}-{self.course_id}"
    
    def to_dict(self):
        return {
            "id": self.id,
            "course_id": self.course_id,
            "student_id": self.student_id,
            "enrolled_time": self.enrolled_time.isoformat() if self.enrolled_time else None,
            "progress": self.progress,
            "is_active": self.is_active,
            "is_completed": self.is_completed,
            "course": {
                "id": self.course_model.id,
                "title": self.course_model.title
            } if self.course_model else None,
            "student": {
                "id": self.student_model.id,
                # "name": self.student_model.name
            } if self.student_model else None,
        }

class ChapterProgress(Base):
    __tablename__ = "chapter_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student_model.id"))
    chapter_id: Mapped[int] = mapped_column(ForeignKey("chapter_model.id"))
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False)
    start_time: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[DateTime] = mapped_column(DateTime, nullable=True)

    chapter: Mapped["Chapter"] = relationship("Chapter", single_parent=True, cascade="all, delete-orphan")
    student: Mapped["Student"] = relationship("Student")
    
    def __str__(self):
        return f"{self.student_id}-{self.chapter_id}"
    
    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "chapter_id": self.chapter_id,
            "is_completed": self.is_completed,
            "is_locked":self.is_locked,
            "start_time": self.start_time,
            "end_time": self.end_time,
        }
    
    @property
    def duration(self):
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() / 60  # Return duration in minutes
        return None

    
    
class ModuleProgress(Base):
    __tablename__ = "module_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student_model.id"))
    module_id: Mapped[int] = mapped_column(ForeignKey("module_model.id"))
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    start_time: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[DateTime] = mapped_column(DateTime, nullable=True)

    module: Mapped["Module"] = relationship("Module", single_parent=True, cascade="all, delete-orphan")
    student: Mapped["Student"] = relationship("Student")

    def __str__(self):
        return f"{self.student_id}-{self.module_id}"

class StageProgress(Base):
    __tablename__ = "stage_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student_model.id"))
    stage_id: Mapped[int] = mapped_column(ForeignKey("stage_model.id"))
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    start_time: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[DateTime] = mapped_column(DateTime, nullable=True)

    stage: Mapped["Stage"] = relationship("Stage", back_populates="stage_progress", single_parent=True, cascade="all, delete-orphan")
    student: Mapped["Student"] = relationship("Student")

    def __str__(self):
        return f"student{self.student_id}-stage{self.stage_id}"

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "stage_id": self.stage_id,
            "is_completed": self.is_completed,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
        }
