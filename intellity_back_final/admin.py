from sqladmin import Admin, ModelView

from intellity_back_final.models.user_models import User, Teacher, Student, Role, Privilege, SiteUser
from .database import engine


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

def create_admin_app(app):
    admin = Admin(app, engine)
    admin.add_view(UserAdmin)
    admin.add_view(TeacherAdmin)
    admin.add_view(StudentAdmin)
    admin.add_view(RoleAdmin)
    admin.add_view(PrivilegeAdmin)
    admin.add_view(SiteUserAdmin)
    return admin
