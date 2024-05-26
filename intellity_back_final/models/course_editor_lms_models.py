from sqlalchemy import (Boolean
                        , Column
                        , ForeignKey
                        , Integer
                        , String
                        , BigInteger
                        , Text
                        , DateTime)
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
    title = Column(String(30), unique=True)
    description = Column(Text)
    course_views_counter = Column(BigInteger, default=0)
    subscription_counter = Column(BigInteger, default=0)

    category_model = relationship("CourseCategory", back_populates="courses_model")
    teacher_model = relationship("Teacher", back_populates="courses_model")
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
            "category": self.category_model.title if self.category else None,
            "teacher": {
                "name": self.teacher_model.name if self.teacher_model else None,
                "lastname": self.teacher_model.lastName if self.teacher_model else None,
            }
        }

class Chapter(Base):
    __tablename__ = "chapter_model"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("course_model.id", ondelete='CASCADE'))
    title = Column(String(30))
    description = Column(Text)
    sort_index = Column(Integer, default=1)
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
            "title": self.title,
            "description": self.description,
            "modules": self.modules,
            "sort_index": self.sort_index
        }

    def can_start(self, student):
        if not self.previous_chapter:
            return True  # Если нет предыдущей главы, можно начать
        if self.previous_chapter in student.completed_chapters:
            return True  # Если предыдущая глава пройдена, можно начать
        return False


class Module(Base):
    __tablename__ = "module_model"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    chapter_id = Column(Integer, ForeignKey("chapter_model.id", ondelete='CASCADE'))
    title = Column(String(30))
    description = Column(Text)

    chapter = relationship("Chapter", back_populates="modules")
    stages = relationship("Stage", back_populates="module", cascade="all, delete-orphan")

    def __str__(self):
        return f'{self.title}'

    def to_dict(self):
        return {
            "id": self.id,
            "chapter_id": self.chapter_id,
            "title": self.title,
            "description": self.description
        }


class Stage(Base):
    __tablename__ = "stage_model"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type = Column(String(20))
    module_id = Column(Integer, ForeignKey("module_model.id", ondelete='CASCADE'))
    title = Column(String(30))
    questions = relationship("Question", back_populates="quiz")

    module = relationship("Module", back_populates="stages")

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
    __mapper_args__ = {'polymorphic_identity': 'classic'}
    html_code_text = Column(String)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_dict(self):
        lesson_data = {
            "html_code_text": self.html_code_text if self.html_code_text is not None else "",
        }
        return {
            **super().to_dict(),
            "lesson": lesson_data
        }


class VideoLesson(Stage):
    __mapper_args__ = {'polymorphic_identity': 'video'}
    video_link = Column(String)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_dict(self):
        lesson_data = {
            "video_link": self.video_link if self.video_link is not None else ""
        }
        return {
            **super().to_dict(),
            "lesson": lesson_data
        }


class ProgrammingLesson(Stage):
    __mapper_args__ = {'polymorphic_identity': 'programming'}
    code_string = Column(String)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_dict(self):
        lesson_data = {
            "code_string": self.code_string if self.code_string is not None else ""
        }
        return {
            **super().to_dict(),
            "lesson": lesson_data
        }


class QuizLesson(Stage):
    __mapper_args__ = {'polymorphic_identity': 'quiz'}
    questions = relationship("Question", back_populates="quiz")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_dict(self):
        return super().to_dict()


class Question(Base):
    __tablename__ = "questions_questions"
    id = Column(Integer, primary_key=True)
    question_text = Column(String)
    order = Column(Integer)
    quiz_id = Column(Integer, ForeignKey("stage_model.id"))
    is_true_answer = Column(Boolean)
    quiz = relationship("QuizLesson", back_populates="questions")

    def to_dict(self):
        return {
            "id": self.id,
            "question_text": self.question_text,
            "order": self.order,
            "is_true_answer": self.is_true_answer
        }


# # class StagePass(models.Model):
# #     stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name='stage_stage_pass')
# #     student = models.ForeignKey(Student, on_delete=models.CASCADE,related_name='stage_passed_students')
# #     is_passed = models.BooleanField(default=False)

# #     class Meta:
# #         verbose_name = 'пройденные уроки'
# #         verbose_name_plural = 'пройденные уроки'


# #     def __str__(self):
# #         return f"{self.student}-{self.stage}-{self.is_passed}"   


# # class CourseRating(models.Model):
# #     course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='rating_courses')
# #     student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='rating_students')
# #     rating = models.PositiveBigIntegerField(default=0)
# #     review = models.TextField(null=True)
# #     review_time = models.DateTimeField(auto_now_add=True)

# #     class Meta:
# #         verbose_name = 'Рейтинг курса'
# #         verbose_name_plural = 'Рейтинги курсов'

# #     def __str__(self):
# #         return f"{self.course}-{self.student}-{self.rating}"   
    

# # class TotalStudentScore(models.Model):
# #     student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='total_score_students')
# #     total_student_score = models.PositiveBigIntegerField(default=0)

# #     class Meta:
# #         verbose_name = 'Баллы ученика'
# #         verbose_name_plural = 'Баллы ученика'

# #     def __str__(self):
# #         return f"{self.student}-{self.total_student_score}"       


# # class TotalStudentEnergy(models.Model):
# #     student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='total_energy_students')
# #     total_student_energy = models.PositiveBigIntegerField(default=100)

# #     class Meta:
# #         verbose_name = 'Энергия ученика'
# #         verbose_name_plural = 'Энергия ученика'

# #     def __str__(self):
# #         return f"{self.student}-{self.total_student_energy}"       
    

# # class FavoriteCourse(models.Model):
# #     course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='favorite_courses')
# #     student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='favorite_students')
# #     is_favorite = models.BooleanField(default=False)

# #     class Meta:
# #         verbose_name = 'Избранный курс'
# #         verbose_name_plural = 'Избранные курсы'

# #     def __str__(self):
# #         return f"{self.course}-{self.student}"   
    

# # class TaskForStudentsFromTeacher(models.Model):
# #     student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='tasks_student')
# #     teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='tasks_teacher')
# #     complete_status = models.BooleanField(default=False, null=True)
# #     title = models.CharField(max_length=150)
# #     detail = models.TextField(null=True)
# #     add_time = models.DateTimeField(auto_now_add=True, null=True)

# #     class Meta:
# #         verbose_name = 'Упражнения для ученика'
# #         verbose_name_plural = 'Упражнение для ученика'

# #     def __str__(self):
# #         return f"{self.title}"   
    

# # class Notification(models.Model):
# #     teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True)
# #     student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
# #     notification_text= models.TextField(verbose_name='Notification Text')
# #     notification_subject= models.CharField(max_length=150, verbose_name='Notification Subject', null=True)
# #     notification_for= models.CharField(max_length=150, verbose_name='Notification For', null=True)
# #     notification_created_time = models.DateTimeField(auto_now_add=True)
# #     notification_read_status = models.BooleanField(default=False, verbose_name='Notification Status')

# #     class Meta:
# #         verbose_name = 'Оповещение'
# #         verbose_name_plural = 'Оповещения'


# # class StudyMaterial(models.Model):
# #     course = models.ForeignKey(Course, on_delete=models.CASCADE)
# #     title = models.CharField(max_length=150)
# #     description = models.TextField()
# #     upload = models.FileField(upload_to='study_material/', null=True)
# #     comment = models.TextField(blank=True, null=True)

# #     class Meta:
# #         verbose_name = 'Материалы для курса'
# #         verbose_name_plural = 'Материалы для курса'

# #     def __str__(self):
# #         return self.title
        


