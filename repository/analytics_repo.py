from sqlalchemy.orm import Session
from sqlalchemy.sql import func, cast
from sqlalchemy.types import BigInteger
from decimal import Decimal
from models.network_data import NetworkData


class Analytics:
    def __init__(self, db: Session):
        self.db = db

    def bytes_to_gb(self, byte_value) -> float:
        if isinstance(byte_value,Decimal):
            byte_value = float(byte_value)
            print(byte_value)
        return byte_value / (1024 ** 3)

    def top_10_sources(self, limit: int = 10):
        query = (
            self.db.query(
                NetworkData.src_ip,
                func.sum(cast(NetworkData.bytes, BigInteger)).label("total_bytes")
            )
            .filter(~NetworkData.src_ip.like("0.%"))
            .group_by(NetworkData.src_ip)
            .order_by(func.sum(cast(NetworkData.bytes, BigInteger)).desc())
            .limit(limit)
        )
        result = query.all()

        # Convert result to float for validation compatibility
        return [
            {
                "src_ip": row.src_ip,
                "total_bytes_gbs": round(self.bytes_to_gb((row.total_bytes)),2),
            }
            for row in result
        ]

    def top_10_destinations(self, limit: int = 10):
        query = (
            self.db.query(
                NetworkData.dest_ip,
                func.sum(cast(NetworkData.bytes, BigInteger)).label("total_bytes")
            )
            .filter(~NetworkData.dest_ip.like("0.%"))
            .group_by(NetworkData.dest_ip)
            .order_by(func.sum(cast(NetworkData.bytes, BigInteger)).desc())
            .limit(limit)
        )
        result = query.all()

        return [
            {
                "dest_ip": row.dest_ip,
                "total_bytes_gbs": round(self.bytes_to_gb(float(row.total_bytes)),2),
            }
            for row in result
        ]

    def protocol_statisticss(self):
        query = (
            self.db.query(
                NetworkData.protocol,
                func.count().label("total_flows"),
                func.sum(cast(NetworkData.bytes, BigInteger)).label("total_bytes"),
                func.sum(cast(NetworkData.packets, BigInteger)).label("total_packets"),
            )
            .group_by(NetworkData.protocol)
        )

        result = query.all()
        import pdb;
        return [
            {
                "protocol": row.protocol,
                "total_flows": row.total_flows,
                "total_bytes_gb": round(self.bytes_to_gb(float(row.total_bytes)), 2) if row.total_bytes else 0.0,
                "total_packets": int(row.total_packets) if row.total_packets else 0,
            }
            for row in result
        ]