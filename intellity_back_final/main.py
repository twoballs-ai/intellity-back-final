from typing import Union
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, RedirectResponse
from .routers.lms import lms_views
from .routers.user import user_views
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Optional
import jwt
import bcrypt


app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/token")

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









app.include_router(lms_views, prefix="/api/v1/lms", tags=["основной функционал lms"], dependencies=[Depends(oauth2_scheme)])
app.include_router(user_views, prefix="/api/v1/user", tags=["основной функционал для работы с пользователями"])

if __name__ == "__main__":
    uvicorn.run("intellity_back_final.main:app", host="0.0.0.0", port=8001, reload=True)

