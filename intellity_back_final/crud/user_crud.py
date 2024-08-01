from sqlalchemy.orm import Session
from ..models import user_models
from ..schemas import lms_schemas

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
    user = db.query(user_models.User).filter(user_models.User.id == user_id).first()
    if not user:
        return None

    # Сопоставление типа пользователя с соответствующими моделями
    model_mapping = {
        'teacher_model': user_models.Teacher,
        'student_model': user_models.Student,
        'site_user_model': user_models.SiteUser,
    }

    # Получение модели в зависимости от типа
    user_model = model_mapping.get(user.type)

    if user_model:
        print(f"{user.type} found")
        return db.query(user_model).filter(user_model.id == user_id).first()
    else:
        print("Unknown user type")
        return None
    


def get_user_by_email(db: Session, email: str):
    return db.query(user_models.User).filter(user_models.User.email == email).first()

def get_teacher_by_user_id(db: Session, user_id: int):
    return db.query(user_models.Teacher).filter(user_models.Teacher.id == user_id).first()

def create_site_user(db: Session, email: str, password: str):
    password_hash = user_models.User.create_password_hash(password)

    db_site_user = user_models.SiteUser(email=email, password_hash=password_hash)
    db.add(db_site_user)
    db.commit()
    db.refresh(db_site_user)
    return db_site_user