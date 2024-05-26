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

    courses_model = relationship("Course", back_populates="teacher_model")

    __mapper_args__ = {
        'polymorphic_identity': 'teacher_model',
    }

    def __str__(self):
        return str(self.id)


class Student(User):
    __tablename__ = "student_model"

    id = Column(Integer, ForeignKey('user_model.id'), primary_key=True)
    interested_categories = Column(Text)

    chapter_progress = relationship("ChapterProgress", back_populates="student")
    module_progress = relationship("ModuleProgress", back_populates="student")
    stage_progress = relationship("StageProgress", back_populates="student")
    
    enrollments_model = relationship("CourseEnrollment", back_populates="student_model")

    __mapper_args__ = {
        'polymorphic_identity': 'student_model',
    }

    def __str__(self):
        return str(self.id)