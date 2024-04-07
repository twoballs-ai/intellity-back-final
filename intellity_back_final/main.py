from typing import Union

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, RedirectResponse
from .routers.lms import lms_views
from .routers.user import user_views
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


app.include_router(lms_views, prefix="/api/v1/lms", tags=["основной функционал lms"])
app.include_router(user_views, prefix="/api/v1/user", tags=["основной функционал для работы с пользователями"])

