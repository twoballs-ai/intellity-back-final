from typing import Union
import uvicorn
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, FileResponse
from intellity_back_final.admin import create_admin_app
from .routers.lms import lms_views
from .routers.user import user_views
from .routers.learning_course import study_course_views
from .routers.course_checkers import study_course_checker_views
from .routers.basic_lms_routers import basic_handle_views
from .routers.blog_routers import blog_views
from fastapi.security import OAuth2PasswordBearer
from .auth import oauth2_scheme
import intellity_back_final.handlers  # For registering event handlers
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Create the admin interface
create_admin_app(app)

@app.get("/")
def docs():
    return RedirectResponse("/docs")

@app.get("/r")
def redoc():
    return RedirectResponse("/redoc")

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["https://backend.intellity.ru"],
    # allow_origins=["*"], 
    allow_origins=["https://intellity.ru", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploaded_directory", StaticFiles(directory="uploaded_directory"), name="uploaded_directory")

@app.get("/sitemap.xml", response_class=FileResponse)
async def sitemap():
    return "sitemap.xml"

app.include_router(user_views, prefix="/api/v1/user", tags=["User management"])
app.include_router(lms_views, prefix="/api/v1/lms", tags=["LMS - Course creation"], dependencies=[Depends(oauth2_scheme)])
app.include_router(study_course_views, prefix="/api/v1/study", tags=["LMS - Course enrollment and completion"], dependencies=[Depends(oauth2_scheme)])
app.include_router(study_course_checker_views, prefix="/api/v1/course_checkers", tags=["LMS - Course checkers"], dependencies=[Depends(oauth2_scheme)])
app.include_router(basic_handle_views, prefix="/api/v1/base", tags=["LMS - General requests for unauthorized users"])
app.include_router(blog_views, prefix="/api/v1/blog", tags=["Blog"])

if __name__ == "__main__":
    uvicorn.run("intellity_back_final.main:app", host="0.0.0.0", port=8001, reload=True)
