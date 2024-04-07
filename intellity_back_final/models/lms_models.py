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

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(30), unique=True)
    description: Mapped[str] = mapped_column(Text)

    class Meta:
        verbose_name = '1. категория курса'
        verbose_name_plural = '1. категории курсов'

    def __str__(self):
        return self.title
    
    def to_dict(self):
        return {
            "title": self.title,
            "message": self.description,
        }

 

class Course(Base):
    __tablename__ = "course_model"    
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    category: Mapped[int] = mapped_column(ForeignKey("course_category_model.id")) 
    teacher_id = Column(Integer, ForeignKey("teacher_model.id", ondelete='CASCADE'))
    title: Mapped[str] = mapped_column(String(30), unique=True)
    description: Mapped[str] = mapped_column(Text)
    # technologicals = Column(Text, nullable=True)
    course_views: Mapped[int] = mapped_column(BigInteger, default=0)

    # chapter_model = relationship("Chapter", back_populates="course_model")
    chapter_model: Mapped[List["Chapter"]] = relationship(
    back_populates="course_model", cascade="all, delete-orphan"
    )

# class CourseEnroll(Base):
#     __tablename__ = "course_enroll_model"  

#     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
#     course = Column(Integer, ForeignKey("course_model.id"))
#     student =  Column(Integer, ForeignKey("user_model.id"))
#     enrolled_time = Column(DateTime, server_default=func.now(), index=True)



#     def __str__(self):
#         return f"{self.course}-{self.student}"  

# #     class Meta:
# #         verbose_name = 'Студент подписанный на курс'
# #         verbose_name_plural = 'Студенты подписанные на курсы'

# #     def __str__(self):
# #         return f"{self.course}-{self.student}"   
# # # Эта функция необходима для перехода на первый модуль первого урока курса 
# #     def student_course_first_module(self):
# #         student_course_first_module = Chapter.objects.filter(course= self.course).first()
# #         course_module = Module.objects.filter(chapter = student_course_first_module).values_list('pk', flat=True).first()
# #         first_module_stage_pk = Stage.objects.filter(module = course_module).values_list('pk', flat=True).first()
# #         return {'first_module_pk':course_module,'first_stage_pk':first_module_stage_pk}
    

class Chapter(Base):
    __tablename__ = "chapter_model"  

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("course_model.id", ondelete='CASCADE')) 
    title: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(Text)
    course_model: Mapped["Course"] = relationship(back_populates="chapter_model")
    
    module_rel_model: Mapped[List["Module"]] = relationship(
    back_populates="chapter_rel_model", cascade="all, delete-orphan"
    )

    class Meta:
        verbose_name = '3. Глава'
        verbose_name_plural = '3. Глава'

    def __str__(self):
        return self.title
    
    def to_dict(self):
        return {
            "id":self.id,
            "title": self.title,
            "description": self.description,
            "modules":self.module_rel_model
        }
    def __repr__(self):
        return f"{self.title}"


class Module(Base):
    __tablename__ = "module_model"  

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    # course: Mapped[int] = mapped_column(ForeignKey("course_model.id", ondelete='CASCADE')) 
    chapter_id: Mapped[int] = mapped_column(ForeignKey("chapter_model.id", ondelete='CASCADE')) 
    title: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(Text)
    
    chapter_rel_model: Mapped["Chapter"] = relationship(back_populates="module_rel_model")
    stage_rel_model: Mapped[List["Stage"]] = relationship(
    back_populates="module_rel_model", cascade="all, delete-orphan"
    )
    class Meta:
        verbose_name = '4. модули'
        verbose_name_plural = '4. модули'

    def __str__(self):
        return f'{self.title}'    
    
    def to_dict(self):
        return {
            "id":self.id,
            "chapter_id":self.chapter_id,
            "title": self.title,
            "description": self.description
        }
    
    
class Stage(Base):
    __tablename__ = "stage_model"  

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    # course = Column(Integer, ForeignKey("course_model.id", ondelete='CASCADE'))
    module_id: Mapped[int] = mapped_column(ForeignKey("module_model.id", ondelete='CASCADE')) 
    title: Mapped[str] = mapped_column(String(30))

    module_rel_model: Mapped["Module"] = relationship(back_populates="stage_rel_model")
    items = relationship("StageItem", back_populates="stage", uselist=False)
    class Meta:
        verbose_name = '5. этап'
        verbose_name_plural = '5. этап'

    # def get_stage_pass_status(self):
    #     get_stage_pass_status = StagePass.objects.filter(stage=self.pk)
    #     return serializers.serialize('json',get_stage_pass_status)
    
    def __str__(self):
        return f"{self.id}"
       
    def to_dict(self):
        item_data = {}
        if self.items:
            print("dfssssf")
            if isinstance(self.items, ClassicLesson):
                print("dff")
                item_data = {
                    "type": self.items.type,
                    "id": self.items.id,
                    "stage_id": self.items.stage_id,
                    "text": self.items.text
                }
            else:
                item_data = {
                    "type": self.items.type,
                    "id": self.items.id,
                    "stage_id": self.items.stage_id
                }
        return {
            "id": self.id,
            "module_id": self.module_id,
            "title": self.title,
            "items": self.items if self.items != None else {},
        }

class StageItem(Base):
    __tablename__ = "stage_items"
    id = Column(Integer, primary_key=True)
    type = Column(String) # Тип элемента: classic, video, quiz
    stage_id = Column(Integer, ForeignKey("stage_model.id"))
    stage = relationship("Stage", back_populates="items")
    __mapper_args__ = {
        'polymorphic_identity':'base',
        'polymorphic_on':'type'
    }

class ClassicLesson(StageItem):
    __mapper_args__ = {'polymorphic_identity':'classic'}
    text = Column(String) 
    # Дополнительные поля и связи для классика

class VideoLesson(StageItem):
    __mapper_args__ = {'polymorphic_identity':'video'}
    # Дополнительные поля и связи для видео

class QuizLesson(StageItem):
    __mapper_args__ = {'polymorphic_identity':'quiz'}
    # Дополнительные поля и связи для викторины

class ProgrammingLesson(StageItem):
    __mapper_args__ = {'polymorphic_identity':'programming'}



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
        


