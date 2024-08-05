from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
import os
from dotenv import load_dotenv

from intellity_back_final.models.blog_models import Blog
from intellity_back_final.models.site_utils_models import ActionLog
from intellity_back_final.models.user_models import User, Teacher, Student, Role, Privilege, SiteUser
from intellity_back_final.models.course_editor_lms_models import Course
from intellity_back_final.database import SessionLocal, engine
import bcrypt
load_dotenv()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



class TeacherAdmin(ModelView, model=Teacher):
    column_list = [Teacher.id, Teacher.email, Teacher.name, Teacher.lastName, Teacher.qualification, Teacher.skills]


class CourseAdmin(ModelView, model=Course):
    column_list = [Course.id, Course.category, Course.teacher_id, Course.title, Course.description, Course.status_id] 


class StudentAdmin(ModelView, model=Student):
    column_list = [Student.id, Student.email, Student.interested_categories]


class RoleAdmin(ModelView, model=Role):
    column_list = [Role.id, Role.name, Role.privileges]


class PrivilegeAdmin(ModelView, model=Privilege):
    column_list = [Privilege.id, Privilege.name]


class SiteUserAdmin(ModelView, model=SiteUser):
    form_columns = [SiteUser.email,SiteUser.password_hash, SiteUser.role, SiteUser.is_superuser]
    column_list = [SiteUser.id, SiteUser.email, SiteUser.password_hash, SiteUser.type, SiteUser.role, SiteUser.is_superuser, SiteUser.is_active, SiteUser.is_verified]
    
    # form_edit_rules = [SiteUser.email]


class BlogAdmin(ModelView, model=Blog):
    column_list = [Blog.id, Blog.title, Blog.content, Blog.category, Blog.created_at, Blog.updated_at]

class LoggingAdmin(ModelView, model=ActionLog):
    column_list = [ActionLog.id, ActionLog.user_id, ActionLog.action, ActionLog.timestamp]

class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form.get("username"), form.get("password")

        if not username or not password:
            return False

        # Use synchronous database access within an async context
        db = next(get_db())
        user = db.query(User).filter(User.email == username).first()
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return False

        # Ensure user type is 'site_user_model'
        if user.type != 'site_user_model':
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

        # Ensure user type is 'site_user_model'
        if user.type != 'site_user_model':
            return False

        return True

def create_admin_app(app):
    authentication_backend = AdminAuth(secret_key=os.getenv('SECRET_KEY'))
    admin = Admin(app, engine, authentication_backend=authentication_backend)
    admin.add_view(TeacherAdmin)
    admin.add_view(StudentAdmin)
    admin.add_view(RoleAdmin)
    admin.add_view(PrivilegeAdmin)
    admin.add_view(SiteUserAdmin)
    admin.add_view(BlogAdmin)
    admin.add_view(LoggingAdmin)
    admin.add_view(CourseAdmin)
    
    return admin