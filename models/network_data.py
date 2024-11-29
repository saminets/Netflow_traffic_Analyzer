from sqlalchemy import Column, Enum, Text,Integer,String
from core.database import Base
from models.base import BaseMixin

class NetworkData(Base, BaseMixin):
    __tablename__ = "network_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dest_ip = Column(Text, nullable=True)
    src_ip = Column(Text, nullable=True)
    bytes = Column(Text, nullable=True)
    packets = Column(Text, nullable=True)
    src_port = Column(Text, nullable=True)
    direction = Column(Enum("inbound", "outbound"), nullable=True)
    protocol = Column(String(20), nullable=True)
    dst_port = Column(Text, nullable=True)
    application = Column(String(255), nullable=True)
