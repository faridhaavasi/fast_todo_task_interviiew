from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, DateTime
import datetime
from app.core.database import Base


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.now())
    password = Column(String(50), nullable=False)

