from sqlalchemy.orm import Session

from ..models import user_models
from ..schemas import lms_schemas


def create_teacher(db: Session, qualification:str, skills:str):
    db_teacher = user_models.Teacher(qualification=qualification, skills=skills)
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher

def create_student(db: Session, interested_categories:str):
    db_student = user_models.Student(interested_categories=interested_categories)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student
