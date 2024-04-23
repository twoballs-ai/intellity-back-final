from sqlalchemy import (Boolean
                        , Column
                        , ForeignKey
                        , Integer
                        , String
                        , BigInteger
                        , Text)
from sqlalchemy.orm import relationship
import bcrypt
from ..database import Base


class User(Base):
    __tablename__ = 'user_model'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(64), index=True, unique=True)
    password_hash = Column(String(64))
    type = Column(String(64))


    __mapper_args__ = {
        'polymorphic_identity': 'user_model',
        'polymorphic_on': 'type'
    }

           
    @classmethod
    def create_password_hash(cls, password):
        """
        Создает соленый хеш пароля.
        """
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        return password_hash.decode('utf-8')

    def set_password(self, password):
        """
        Устанавливает соленый хеш для пароля.
        """
        self.password_hash = self.create_password_hash(password)
        
        

 

class Teacher(User):
    __tablename__ = "teacher_model"  

    id = Column(Integer, ForeignKey('user_model.id'), primary_key=True)
    name = Column(String(64))
    lastName = Column(String(64))
    qualification = Column(String)
    skills = Column(Text)

    __mapper_args__ = {
        'polymorphic_identity': 'teacher_model',
    }

    def __str__(self):
        return str(self.id)

    # class Meta:
    #     verbose_name = 'учитель'
    #     verbose_name_plural = 'учителя'
    #     permissions = (("sample_permission", "can change sth of sth"),)

    # def skill_list(self):
    #     skill_list=self.skills.split(',')
    #     return skill_list        

    # def total_teacher_courses(self):
    #     total_courses= lms.models.Course.objects.filter(teacher = self).count()
    #     return total_courses
    
    # def total_teacher_chapters(self):
    #     total_chapters= lms.models.Chapter.objects.filter(course__teacher= self).count()
    #     return total_chapters

    # def total_teacher_students(self):
    #     total_students= lms.models.CourseEnroll.objects.filter(course__teacher = self).count()
    #     return total_students
    


class Student(User):
    __tablename__ = "student_model"    
    
    id = Column(Integer, ForeignKey('user_model.id'), primary_key=True) 
    interested_categories = Column(Text)
    
    __mapper_args__ = {
        'polymorphic_identity': 'student_model',
    }

    def __str__(self):
        return str(self.id)

    # class Meta:
    #     verbose_name = 'ученик'
    #     verbose_name_plural = 'ученики'
    #     permissions = (("sample_permission", "can change sth in sth"),)

    # def total_student_score(self):
    #     student_score= lms.models.TotalStudentScore.objects.get_or_create(student=self)[0]
    #     student_score = student_score.total_student_score
    #     return student_score
    
    # def total_student_energy(self):
    #     student_energy= lms.models.TotalStudentEnergy.objects.get_or_create(student=self)[0]
    #     print(student_energy)
    #     student_energy = student_energy.total_student_energy
    #     print(student_energy)
    #     return student_energy

    # def total_student_enroll_courses(self):
    #     enrolled_courses= lms.models.CourseEnroll.objects.filter(student = self).count()
    #     return enrolled_courses
    
    # def total_favorite_courses(self):
    #     favorite_course= lms.models.FavoriteCourse.objects.filter(student= self).count()
    #     return favorite_course
    
    # def total_completed_tasks(self):
    #     completed_task= lms.models.TaskForStudentsFromTeacher.objects.filter(student = self, complete_status=True).count()
    #     return completed_task    

    # def total_pending_tasks(self):
    #     pending_task= lms.models.TaskForStudentsFromTeacher.objects.filter(student = self, complete_status=False).count()
    #     return pending_task   