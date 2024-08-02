from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum

from intellity_back_final.database import Base

class LogType(Base):
    __tablename__ = "log_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    action_logs = relationship("ActionLog", back_populates="log_type")

    def __str__(self):
        return self.name

class ActionLog(Base):
    __tablename__ = "action_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_model.id"))
    action = Column(String, index=True)
    log_type_id = Column(Integer, ForeignKey("log_types.id"))
    object_id = Column(String, index=True)
    model_name = Column(String, index=True)  # New column to store the model or table name
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    log_type = relationship("LogType", back_populates="action_logs")

    def __str__(self):
        return (f"ActionLog(id={self.id}, user_id={self.user_id}, action={self.action}, "
                f"log_type={self.log_type.name}, object_id={self.object_id}, "
                f"model_name={self.model_name}, timestamp={self.timestamp})")