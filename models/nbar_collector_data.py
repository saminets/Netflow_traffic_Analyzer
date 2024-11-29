from sqlalchemy import Column, Integer, String, BigInteger
from core.database import Base
from models.base import BaseMixin

class NbarCollectorData(Base, BaseMixin):
    __tablename__ = "nbar_collector_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    src_ip = Column(String(45), nullable=True)
    dst_ip = Column(String(45), nullable=True)
    src_port = Column(Integer, nullable=True)
    application_id = Column(Integer, nullable=True)
    protocol = Column(Integer, nullable=True)
    packet_count = Column(BigInteger, nullable=True)
    in_bytes = Column(BigInteger, nullable=True)
    out_bytes = Column(BigInteger, nullable=True)
    timestamp = Column(BigInteger, nullable=True)
