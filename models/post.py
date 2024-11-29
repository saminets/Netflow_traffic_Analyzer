from sqlalchemy import Column, Integer, String, Boolean
from core.database import Base
from models.base import BaseMixin

class Post(Base, BaseMixin):
    __tablename__ = "post"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_token = Column(String(255), nullable=False)
    title = Column(String(255), nullable=True)
    content = Column(String(255), nullable=True)
    is_published = Column(Boolean, nullable=False)
