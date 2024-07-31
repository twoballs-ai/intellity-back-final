# @app.get("/some-protected-endpoint")
# @require_roles(['Admin', 'Editor'])
# async def some_protected_endpoint(request: Request):
#     user = request.state.user
#     # Your endpoint logic here
#     return {"message": "You have access to this endpoint"}

# @app.post("/another-endpoint")
# async def another_endpoint(request: Request):
#     user = request.state.user
#     if is_teacher(user):
#         # Logic specific to teachers
#         pass
#     elif is_student(user):
#         # Logic specific to students
#         pass
#     elif is_site_user(user):
#         user_role = user.role.name if user.role else None
#         if user_role == 'Admin':
#             # Logic for admin site users
#             pass
#         elif user_role == 'Editor':
#             # Logic for editor site users
#             pass
#         else:
#             raise HTTPException(status_code=403, detail="Unauthorized user role")
#     else:
#         raise HTTPException(status_code=403, detail="Unauthorized user type")
#     return {"message": "Action performed"}