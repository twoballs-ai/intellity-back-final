from sqlalchemy import (Boolean, Column, ForeignKey, Integer, String, Table, Text)
from sqlalchemy.orm import relationship
import bcrypt
from ..database import Base

role_privilege_association = Table(
    'role_privilege_association',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('role_model.id')),
    Column('privilege_id', Integer, ForeignKey('privilege_model.id'))
)

class User(Base):
    __tablename__ = 'user_model'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(64), index=True, unique=True)
    password_hash = Column(String(64))
    type = Column(String(64))
    is_active = Column(Boolean, default=True)  # Добавляем поле is_active

    blogs = relationship("Blog", back_populates="owner")
    __mapper_args__ = {
        'polymorphic_identity': 'user_model',
        'polymorphic_on': 'type'
    }

    def to_dict(self):
        """
        Convert the user object to a dictionary.
        """
        return {
            "id": self.id,
            "email": self.email,
            "type": self.type,
            "is_active": self.is_active,  # Добавляем is_active в словарь
            # Add more attributes as needed
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

    def to_dict(self):
        """
        Convert the teacher object to a dictionary.
        """
        user_dict = super().to_dict()  # Call the parent method to get the base attributes
        teacher_dict = {
            "name": self.name,
            "lastName": self.lastName,
            "qualification": self.qualification,
            "skills": self.skills,
            # Add other attributes specific to the teacher
        }
        return {**user_dict, **teacher_dict}


class Student(User):
    __tablename__ = "student_model"

    id = Column(Integer, ForeignKey('user_model.id'), primary_key=True)
    interested_categories = Column(Text)
    solved_tasks_count = Column(Integer, default=0)  # Добавлен новый атрибут для счетчика решенных задач
    energy = Column(Integer, default=100)  # Добавлен атрибут для энергии, установленное значение по умолчанию 100

    chapter_progress = relationship("ChapterProgress", back_populates="student")
    module_progress = relationship("ModuleProgress", back_populates="student")
    stage_progress = relationship("StageProgress", back_populates="student")

    enrollments_model = relationship("CourseEnrollment", back_populates="student_model")

    __mapper_args__ = {
        'polymorphic_identity': 'student_model',
    }

    def __str__(self):
        return str(self.id)

    def to_dict(self):
        """
        Convert the student object to a dictionary.
        """
        user_dict = super().to_dict()  # Вызываем метод родительского класса для получения базовых атрибутов
        student_dict = {
            "interested_categories": self.interested_categories,
            "solved_tasks_count": self.solved_tasks_count,
            "energy": self.energy,
            # Добавляем другие атрибуты, специфичные для студента
        }
        return {**user_dict, **student_dict}
    
class Role(Base):
    __tablename__ = "role_model"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(64), unique=True)

    privileges = relationship("Privilege", secondary=role_privilege_association, back_populates="roles")
    admins = relationship("SiteUser", back_populates="role")
    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "privileges": [privilege.to_dict() for privilege in self.privileges],
        }

class Privilege(Base):
    __tablename__ = "privilege_model"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(64), unique=True)

    roles = relationship("Role", secondary=role_privilege_association, back_populates="privileges")

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
        }

class SiteUser(User):
    __tablename__ = "site_user_model"

    id = Column(Integer, ForeignKey('user_model.id'), primary_key=True)
    role_id = Column(Integer, ForeignKey('role_model.id'))

    role = relationship("Role", back_populates="admins")

    __mapper_args__ = {
        'polymorphic_identity': 'site_user_model',
    }

    def __str__(self):
        return str(self.id)

    def to_dict(self):
        user_dict = super().to_dict()
        site_user_dict = {
            "role": self.role.to_dict() if self.role else None,
        }
        return {**user_dict, **site_user_dict}


