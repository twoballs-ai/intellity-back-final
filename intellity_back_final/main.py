from typing import Union
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, RedirectResponse
from .routers.lms import lms_views
from .routers.user import user_views
from .routers.learning_course import study_course_views
from .routers.course_checkers import study_course_checker_views
from .routers.basic_lms_routers import basic_handle_views

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Optional
import jwt
import bcrypt
from fastapi.staticfiles import StaticFiles
from .auth import oauth2_scheme

app = FastAPI()



@app.get("/")
def docs():
    return RedirectResponse("/docs")


@app.get("/r")
def docs():
    return RedirectResponse("/redoc")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://localhost:5173/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/uploaded_directory", StaticFiles(directory="uploaded_directory"), name="uploaded_directory")









app.include_router(user_views, prefix="/api/v1/user", tags=["основной функционал для работы с пользователями"])
app.include_router(lms_views, prefix="/api/v1/lms", tags=["основной функционал lms создание курсов"], dependencies=[Depends(oauth2_scheme)])
app.include_router(study_course_views, prefix="/api/v1/study", tags=["основной функционал lms записи на курс и его прохождения"], dependencies=[Depends(oauth2_scheme)])
app.include_router(study_course_checker_views, prefix="/api/v1/course_checkers", tags=["основной функционал lms проверки курсов на прохождение"], dependencies=[Depends(oauth2_scheme)])
app.include_router(basic_handle_views, prefix="/api/v1/base", tags=["основной функционал lms сов семи доп запросами для неавторизованных пользователей"])




if __name__ == "__main__":
    uvicorn.run("intellity_back_final.main:app", host="0.0.0.0", port=8001, reload=True)

