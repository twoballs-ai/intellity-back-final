from sqlalchemy import (Boolean, Column, ForeignKey, Integer, String, Text, DateTime)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Session
from ..database import Base

from typing import List, Optional
from sqlalchemy.orm import Mapped, mapped_column


class BlogCategory(Base):
    __tablename__ = "blog_category_model"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(100), unique=True)

    blogs = relationship("Blog", back_populates="category")

    def __str__(self):
        return self.title

    def to_dict(self):
        return {
            "title": self.title,
        }
    
    def to_select(self):
        return {
            "value": self.id,
            "label": self.title,
        }


class Blog(Base):
    __tablename__ = "blog_model"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(30))
    content = Column(Text)
    category_id = Column(Integer, ForeignKey('blog_category_model.id'))
    owner_id = Column(Integer, ForeignKey('user_model.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    category = relationship("BlogCategory", back_populates="blogs")
    owner = relationship("User", back_populates="blogs")

    def __str__(self):
        return self.title

    def to_dict(self):
        return {
            "id":self.id,
            "title": self.title,
            "content": self.content,
            "category":self.category.title,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "author": self.owner.email
        }

 