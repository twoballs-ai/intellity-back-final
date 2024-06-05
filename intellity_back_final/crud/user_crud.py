from sqlalchemy.orm import Session

from ..models import user_models
from ..schemas import lms_schemas
from sqlalchemy.orm import Session
# from . import models
import bcrypt

def create_teacher(db: Session, name: str,lastName:str,  email: str, password: str, qualification: str, skills: str):
    # Создаем соленый хеш пароля
    password_hash = user_models.User.create_password_hash(password)

    # Создаем учителя и устанавливаем соленый хеш пароля
    db_teacher = user_models.Teacher(name=name, lastName = lastName, email=email, password_hash=password_hash, qualification=qualification, skills=skills)
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher

def create_student(db: Session, email: str, password: str, interested_categories: str):
    # Создаем соленый хеш пароля
    password_hash = user_models.User.create_password_hash(password)

    # Создаем студента и устанавливаем соленый хеш пароля
    db_student = user_models.Student(email=email, password_hash=password_hash, interested_categories=interested_categories)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

def get_user(db: Session, user_id: int):
    return db.query(user_models.User).filter(user_models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(user_models.User).filter(user_models.User.email == email).first()
