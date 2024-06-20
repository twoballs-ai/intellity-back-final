from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from intellity_back_final.models.user_models import User, Teacher, Student, Role, Privilege, SiteUser
from intellity_back_final.database import SessionLocal, engine
import bcrypt
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# SQLAdmin views for admin interface
class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email, User.type, User.is_active]

class TeacherAdmin(ModelView, model=Teacher):
    column_list = [Teacher.id, Teacher.email, Teacher.name, Teacher.lastName, Teacher.qualification, Teacher.skills]

class StudentAdmin(ModelView, model=Student):
    column_list = [Student.id, Student.email, Student.interested_categories]

class RoleAdmin(ModelView, model=Role):
    column_list = [Role.id, Role.name]

class PrivilegeAdmin(ModelView, model=Privilege):
    column_list = [Privilege.id, Privilege.name]

class SiteUserAdmin(ModelView, model=SiteUser):
    column_list = [SiteUser.id, SiteUser.email, SiteUser.role_id]

class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        db = next(get_db())
        user = db.query(User).filter(User.email == username).first()
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return False

        request.session.update({"user_id": user.id})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        user_id = request.session.get("user_id")
        if not user_id:
            return False

        db = next(get_db())
        user = db.query(User).get(user_id)
        if not user:
            return False

        return True

def create_admin_app(app):
    authentication_backend = AdminAuth(secret_key="your_secret_key_here")
    admin = Admin(app, engine, authentication_backend=authentication_backend)
    admin.add_view(UserAdmin)
    admin.add_view(TeacherAdmin)
    admin.add_view(StudentAdmin)
    admin.add_view(RoleAdmin)
    admin.add_view(PrivilegeAdmin)
    admin.add_view(SiteUserAdmin)
    return admin