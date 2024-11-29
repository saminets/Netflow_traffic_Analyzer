from sqlalchemy import Column, Integer, ForeignKey
from core.database import Base
from models.base import BaseMixin

class PostTag(Base, BaseMixin):
    __tablename__ = "post_tag"

    id = Column(Integer, primary_key=True, autoincrement=False)
    post_id = Column(Integer, ForeignKey("post.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tag.id"), nullable=False)
