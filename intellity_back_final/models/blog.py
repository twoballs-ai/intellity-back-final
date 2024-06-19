from sqlalchemy import (Boolean
                        , Column
                        , ForeignKey
                        , Integer
                        , String
                        , BigInteger
                        , Text
                        , DateTime)
from sqlalchemy import Enum as SQLAlchemyEnum
from enum import Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.orm import Session
from ..database import Base

from typing import List
from typing import Optional

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column



class BlogCategory(Base):
    __tablename__ = "blog_category_model"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(30), unique=True)

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
    title = Column(String(30), unique=True)
    content = Column(Text)
    category_id = Column(Integer, ForeignKey('blog_category_model.id'))
    owner_id = Column(Integer, ForeignKey('teacher_model.id'))

    category = relationship("BlogCategory", back_populates="blogs")
    owner = relationship("Teacher", back_populates="blogs")

    def __str__(self):
        return self.title

    def to_dict(self):
        return {
            "title": self.title,
            "content": self.content,
        }


    def __str__(self):
        return self.title

    def to_dict(self):
        return {
            "title": self.title,
            "message": self.description,
        }
