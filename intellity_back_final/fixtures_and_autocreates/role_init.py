from sqlalchemy.orm import Session
from intellity_back_final.models.user_models import Privilege, Role

def initialize_roles_and_privileges(db: Session):
    # Check if roles already exist
    if db.query(Role).first():
        print("Roles and privileges are already initialized.")
        return

    # Function to get or create a privilege
    def get_or_create_privilege(name: str):
        privilege = db.query(Privilege).filter_by(name=name).first()
        if not privilege:
            privilege = Privilege(name=name)
            db.add(privilege)
            db.commit()
        return privilege

    # Function to get or create a role
    def get_or_create_role(name: str):
        role = db.query(Role).filter_by(name=name).first()
        if not role:
            role = Role(name=name)
            db.add(role)
            db.commit()
        return role

    # Initialize privileges
    privilege_names = [
        "Create Content", "Edit Content", "Delete Content",
        "Manage Users", "Manage Roles", "Manage Privileges",
        "View Reports", "Change Settings"
    ]

    privileges = [get_or_create_privilege(name) for name in privilege_names]

    # Initialize roles
    role_names = ["Administrator", "Moderator", "User", "Guest"]
    roles = [get_or_create_role(name) for name in role_names]

    # Assign privileges to roles
    admin_role = next(role for role in roles if role.name == "Administrator")
    moderator_role = next(role for role in roles if role.name == "Moderator")
    user_role = next(role for role in roles if role.name == "User")
    guest_role = next(role for role in roles if role.name == "Guest")

    admin_role.privileges = privileges
    moderator_role.privileges = [
        p for p in privileges if p.name in ["Create Content", "Edit Content", "Delete Content", "View Reports"]
    ]
    user_role.privileges = [p for p in privileges if p.name in ["Create Content", "Edit Content"]]
    guest_role.privileges = [p for p in privileges if p.name == "View Reports"]

    db.commit()
    print("Roles and privileges have been successfully initialized.")
