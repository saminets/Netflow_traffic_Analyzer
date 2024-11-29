from sqlalchemy import Column, Integer, String
from core.database import Base
from models.base import BaseMixin

class ApplicationDataNbar(Base, BaseMixin):
    __tablename__ = "application_data_nbar"

    name = Column(String(255), primary_key=True, nullable=False)
    application_id = Column(Integer, nullable=True)
    category = Column(String(50), nullable=True)
