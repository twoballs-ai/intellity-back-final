# init_db.py
from sqlalchemy.orm import Session

from intellity_back_final.database import SessionLocal
from intellity_back_final.fixtures_and_autocreates.role_init import initialize_roles_and_privileges

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def init_db():
    # Создаем все таблицы


    
    try:
        # Инициализируем роли и привилегии
        initialize_roles_and_privileges(db: Session = Depends(get_db))
        print("Роли и привилегии успешно инициализированы.")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
