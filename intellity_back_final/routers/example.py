# @app.get("/teacher")
# def read_teacher_data(current_user: dict = Depends(type_checker(["teacher"]))):
#     return {"msg": "Welcome, teacher!"}

# @app.get("/student")
# def read_student_data(current_user: dict = Depends(type_checker(["student"]))):
#     return {"msg": f"Hello, student {current_user['user_id']}!"}

# @app.get("/siteuser/role-specific")
# def read_siteuser_data(current_user: dict = Depends(role_checker(["admin"]))):
#     return {"msg": f"Hello, siteuser with role admin {current_user['user_id']}!"}
# @user_views.get("/protected-route-admin")
# @role_checker(["Administrator"])
# async def protected_route_admin(current_user: User = Depends(get_current_user)):
#     return {"message": "Hello Admin!", "user": current_user.to_dict()}