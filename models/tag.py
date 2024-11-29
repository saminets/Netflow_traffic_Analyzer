from sqlalchemy import Column, Integer, String
from core.database import Base
from models.base import BaseMixin

class Tag(Base, BaseMixin):
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_token = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(String(255), nullable=True)
