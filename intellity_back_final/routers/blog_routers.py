from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel

from intellity_back_final.models.blog_models import Blog, BlogCategory
from intellity_back_final.models.user_models import User
from intellity_back_final.routers.user import get_current_user
from ..database import SessionLocal
blog_views = APIRouter()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class BlogBase(BaseModel):
    title: str
    content: str
    category_id: int

class BlogCreate(BlogBase):
    pass

class BlogOut(BlogBase):
    id: int
    owner_id: int

class BlogCategoryBase(BaseModel):
    title: str

class BlogCategoryCreate(BlogCategoryBase):
    pass

class BlogCategoryOut(BlogCategoryBase):
    id: int

# Create a new blog post
@blog_views.post("/news/", response_model=BlogOut)
async def create_news(news: BlogCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # print(current_user.type)
    if current_user.type not in ["teacher_model", "owner_model"]:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    db_news = Blog(
        title=news.title,
        content=news.content,
        category_id=news.category_id,
        owner_id=current_user.id
    )
    
    db.add(db_news)
    db.commit()
    db.refresh(db_news)
    
    return db_news


# Read blog posts with pagination
@blog_views.get("/news/")
async def read_news(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    result = db.query(Blog).offset(skip).limit(limit).all()
    news = [category.to_dict() for category in result]
    return JSONResponse(
        content={
            "status": True,
            "data": news,
        },
        status_code=200,
    )

# Read blog categories with pagination
@blog_views.get("/categories/")
async def read_categories(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    result = db.query(BlogCategory).offset(skip).limit(limit).all()
    categories_select = [category.to_select() for category in result]
    
    return JSONResponse(
        content={
            "status": True,
            "data": categories_select,
        },
        status_code=200,
    )

