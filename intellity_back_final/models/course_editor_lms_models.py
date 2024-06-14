from sqlalchemy import (Boolean
                        , Column
                        , ForeignKey
                        , Integer
                        , String
                        , BigInteger
                        , Text
                        , DateTime)
from sqlalchemy import Enum as SQLAlchemyEnum
from enum import Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.orm import Session
from ..database import Base

from typing import List
from typing import Optional

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column



class CourseCategory(Base):
    __tablename__ = "course_category_model"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(30), unique=True)
    description = Column(Text)

    # Define reverse relationship
    courses_model = relationship("Course", back_populates="category_model")

    def __str__(self):
        return self.title

    def to_dict(self):
        return {
            "title": self.title,
            "message": self.description,
        }


    def to_select(self):
        return {
            "value": self.id,
            "label": self.title,
        }


class Course(Base):
    __tablename__ = "course_model"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category = Column(Integer, ForeignKey("course_category_model.id"))
    teacher_id = Column(Integer, ForeignKey("teacher_model.id", ondelete='CASCADE'))
    status_id = Column(Integer, ForeignKey("course_status_model.id"), nullable=False)
    moderation_status_id = Column(Integer, ForeignKey("course_moderation_status_model.id"), nullable=True)
    title = Column(String(30), unique=True)
    description = Column(Text)
    course_views_counter = Column(BigInteger, default=0)
    subscription_counter = Column(BigInteger, default=0)
    cover_image_name = Column(String, index=True)
    total_chapters = Column(BigInteger, default=0)
    total_modules = Column(BigInteger, default=0)
    total_stages = Column(BigInteger, default=0)
    cover_path = Column(String, unique=True, nullable=True)
    category_model = relationship("CourseCategory", back_populates="courses_model")
    teacher_model = relationship("Teacher", back_populates="courses_model")
    status_model = relationship("CourseStatus", back_populates="courses")
    modeation_status_model = relationship("CourseModerationStatus", back_populates="courses")
    chapters = relationship("Chapter", back_populates="course", cascade="all, delete-orphan")
    enrollments_model = relationship("CourseEnrollment", back_populates="course_model")

    def __str__(self):
        return self.title

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "course_views": self.course_views_counter,
            "course_subscription": self.subscription_counter,
            "total_chapters": self.total_chapters,
            "total_modules": self.total_modules,
            "total_stages": self.total_stages,
            "cover_image_name": self.cover_image_name,
            "cover_path": self.cover_path,
            "status": self.status_model.status if self.status_model else None, 
            "moderation_status": self.modeation_status_model.status if self.modeation_status_model else None, # Include the status here
            "category": self.category_model.title if self.category else None,
            "teacher": {
                "name": self.teacher_model.name if self.teacher_model else None,
                "lastname": self.teacher_model.lastName if self.teacher_model else None,
                "id": self.teacher_id if self.teacher_id else None,
            },
        }
    


class CourseStatus(Base):
    __tablename__ = "course_status_model"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    status = Column(String, unique=True, nullable=False)
    courses = relationship("Course", back_populates="status_model")

    def __str__(self):
        return self.status
    
class CourseModerationStatus(Base):
    __tablename__ = "course_moderation_status_model"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    status = Column(String, unique=True, nullable=False)
    courses = relationship("Course", back_populates="modeation_status_model")

    def __str__(self):
        return self.status


class Chapter(Base):
    __tablename__ = "chapter_model"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("course_model.id", ondelete='CASCADE'))
    title = Column(String(30))
    description = Column(Text)
    sort_index = Column(Integer, default=1)
    total_modules_in_chapter = Column(BigInteger, default=0)
    total_stages_in_chapter = Column(BigInteger, default=0)
    is_exam = Column(Boolean, default=False)
    exam_duration_minutes = Column(Integer)
    previous_chapter_id = Column(Integer, ForeignKey("chapter_model.id"))
    previous_chapter = relationship("Chapter", remote_side=[id])

    course = relationship("Course", back_populates="chapters")
    modules = relationship("Module", back_populates="chapter", cascade="all, delete-orphan")

    def __str__(self):
        return self.title

    def to_dict(self):
        return {
            "id": self.id,
            "course_id": self.course_id,
            "title": self.title,
            "description": self.description,
            "modules": [module.to_dict() for module in self.modules],
            "sort_index": self.sort_index,
            "total_modules_in_chapter": self.total_modules_in_chapter, 
            "total_stages_in_chapter": self.total_stages_in_chapter, 
            "is_exam": self.is_exam,
            "exam_duration_minutes": self.exam_duration_minutes,
            "previous_chapter_id": self.previous_chapter_id,

        }

    def can_start(self, student):
        if not self.previous_chapter:
            return True  # If there is no previous chapter, it's the first chapter, so the student can start it
        previous_chapter_progress = next((progress for progress in student.chapter_progress if progress.chapter_id == self.previous_chapter.id), None)
        if not previous_chapter_progress or not previous_chapter_progress.is_completed:
            return False
        if self.previous_chapter.is_exam:
            return previous_chapter_progress.is_completed
        return True



class Module(Base):
    __tablename__ = "module_model"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    chapter_id = Column(Integer, ForeignKey("chapter_model.id", ondelete='CASCADE'))
    title = Column(String(30))
    description = Column(Text)
    sort_index = Column(Integer, default=1)
    total_stages_in_module = Column(BigInteger, default=0)
    chapter = relationship("Chapter", back_populates="modules")
    stages = relationship("Stage", back_populates="module", cascade="all, delete-orphan")

    def __str__(self):
        return f'{self.title}'

    def to_dict(self):
        return {
            "id": self.id,
            "chapter_id": self.chapter_id,
            "title": self.title,
            "description": self.description,
            "sort_index":self.sort_index,
            "total_stages_in_module": self.total_stages_in_module,
        }


class Stage(Base):
    __tablename__ = "stage_model"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type = Column(String(20))
    module_id = Column(Integer, ForeignKey("module_model.id", ondelete='CASCADE'))
    title = Column(String(30))

    module = relationship("Module", back_populates="stages")
    stage_progress = relationship("StageProgress", back_populates="stage") 
    __mapper_args__ = {
        'polymorphic_identity': 'stage_item',
        'polymorphic_on': type
    }

    def __str__(self):
        return f"{self.id}"

    def to_dict(self):
        return {
            "id": self.id,
            "module_id": self.module_id,
            "type": self.type,
            "title": self.title,
        }


class ClassicLesson(Stage):
    __tablename__ = "stage_classic_lessons_model"
    id = Column(Integer, ForeignKey('stage_model.id'), primary_key=True)
    html_code_text = Column(String)

    __mapper_args__ = {'polymorphic_identity': 'classic'}

    def to_dict(self):
        lesson_data = {
            "html_code_text": self.html_code_text if self.html_code_text is not None else "",
        }
        return {
            **super().to_dict(),
            "lesson": lesson_data
        }


class VideoLesson(Stage):
    __tablename__ = "stage_video_lessons_model"
    id = Column(Integer, ForeignKey('stage_model.id'), primary_key=True)
    video_link = Column(String)

    __mapper_args__ = {'polymorphic_identity': 'video'}

    def to_dict(self):
        lesson_data = {
            "video_link": self.video_link if self.video_link is not None else ""
        }
        return {
            **super().to_dict(),
            "lesson": lesson_data
        }


class ProgrammingLesson(Stage):
    __tablename__ = "stage_programming_lessons_model"
    id = Column(Integer, ForeignKey('stage_model.id'), primary_key=True)
    code_string = Column(String)

    __mapper_args__ = {'polymorphic_identity': 'programming'}

    def to_dict(self):
        lesson_data = {
            "code_string": self.code_string if self.code_string is not None else ""
        }
        return {
            **super().to_dict(),
            "lesson": lesson_data
        }


class QuizType(Base):
    __tablename__ = 'quiz_types'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)

class QuizLesson(Stage):
    __tablename__ = "stage_quiz_lessons_model"
    id = Column(Integer, ForeignKey('stage_model.id'), primary_key=True)
    quiz_type_id = Column(Integer, ForeignKey('quiz_types.id'), nullable=True)
    question = Column(String)
    quiz_type = relationship('QuizType')
    answers = relationship("Answer", back_populates="quiz", cascade="all, delete-orphan")
    __mapper_args__ = {'polymorphic_identity': 'quiz'}

    def to_dict(self):
        lesson_data = {
            "question":self.question,
            "quiz_type": self.quiz_type.name if self.quiz_type else None,
            "answers": [answer.to_dict() for answer in self.answers]
        }
        return {
            **super().to_dict(),
            "lesson": lesson_data
        }

    def to_learn_dict(self):
        lesson_data = {
            "question":self.question,
            "quiz_type": self.quiz_type.name if self.quiz_type else None,
            "answers": [answer.to_learn_dict() for answer in self.answers]
        }
        return {
            **super().to_dict(),
            "lesson": lesson_data
        }

class Answer(Base):
    __tablename__ = "quiz_answers_model"
    id = Column(Integer, primary_key=True)
    answer_text = Column(String, nullable=False)
    order = Column(Integer, nullable=False)
    quiz_id = Column(Integer, ForeignKey("stage_quiz_lessons_model.id"), nullable=False)
    is_true_answer = Column(Boolean, nullable=False)
    quiz = relationship("QuizLesson", back_populates="answers")

    def to_dict(self):
        return {
            "id": self.id,
            "answer_text": self.answer_text,
            "order": self.order,
            "is_true_answer": self.is_true_answer,
            "quiz_id":self.quiz_id
        }
    
    def to_learn_dict(self):
        return {
            "id": self.id,
            "answer_text": self.answer_text,
            "order": self.order,
            "quiz_id":self.quiz_id
        }
