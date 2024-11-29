from sqlalchemy.orm import Session
from sqlalchemy.sql import func, cast
from sqlalchemy.types import BigInteger
from decimal import Decimal
from models.network_data import NetworkData
from datetime import datetime, timedelta
from datetime import datetime, timezone
from sqlalchemy import func, cast, BigInteger
from ipaddress import ip_network, ip_address
class Analytics:
    def __init__(self, db: Session):
        self.db = db
        self.five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)

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
            .filter(NetworkData.created_at >= self.five_minutes_ago)
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
            .filter(NetworkData.created_at >= self.five_minutes_ago)
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
            .filter(NetworkData.created_at >= self.five_minutes_ago)
            .group_by(NetworkData.protocol)
        )

        result = query.all()

        return [
            {
                "protocol": row.protocol,
                "total_flows": row.total_flows,
                "total_bytes_gb": round(self.bytes_to_gb(float(row.total_bytes)), 2) if row.total_bytes else 0.0,
                "total_packets": int(row.total_packets) if row.total_packets else 0,
            }
            for row in result
        ]

    def hourly_statistics(self):
        query = (
            self.db.query(
                func.date_format(NetworkData.created_at, '%Y-%m-%d %H:00:00').label("hour"),
                func.sum(cast(NetworkData.bytes, BigInteger)).label("total_bytes"),
                func.sum(cast(NetworkData.packets, BigInteger)).label("total_packets"),
            )
            .group_by(func.date_format(NetworkData.created_at, '%Y-%m-%d %H:00:00'))
            .order_by(func.date_format(NetworkData.created_at, '%Y-%m-%d %H:00:00').desc())
        )

        result = query.all()

        # Convert the query results to a dictionary
        return [
            {
                "hour": row.hour,
                "total_bytes_gb": round(float(row.total_bytes) / (1024 ** 3), 2) if row.total_bytes else 0.0,
                "total_packets": int(row.total_packets) if row.total_packets else 0,
            }
            for row in result
        ]

    def top_10_sourcesport(self, limit: int = 10):
        query = (
            self.db.query(
                NetworkData.src_port,
                func.sum(cast(NetworkData.bytes, BigInteger)).label("total_bytes")
            )
            .filter(NetworkData.created_at >= self.five_minutes_ago)
            .group_by(NetworkData.src_port)
            .order_by(func.sum(cast(NetworkData.bytes, BigInteger)).desc())
            .limit(limit)
        )
        result = query.all()


        # Convert result to float for validation compatibility
        return [
            {
                "source_port": row.src_port,
                "total_bytes_gbs": round(self.bytes_to_gb((row.total_bytes)), 2),
            }
            for row in result
        ]
    def top_10_destinationport(self, limit: int = 10):
        query = (
            self.db.query(
                NetworkData.dst_port,
                func.sum(cast(NetworkData.bytes, BigInteger)).label("total_bytes")
            )
            .filter(NetworkData.created_at >= self.five_minutes_ago)
            .group_by(NetworkData.dst_port)
            .order_by(func.sum(cast(NetworkData.bytes, BigInteger)).desc())
            .limit(limit)
        )
        result = query.all()

        # Convert result to float for validation compatibility
        return [
            {
                "destination_port": row.dst_port,
                "total_bytes_gbs": round(self.bytes_to_gb((row.total_bytes)), 2),
            }
            for row in result
        ]

    def bytes_and_packets_by_duration(self, duration: str):

        now = datetime.now(timezone.utc)
        start_date = None

        # gmt_zone = pytz.timezone("Etc/GMT")
        # start_date = now.replace(tzinfo=pytz.utc).astimezone(gmt_zone)
        # Define start date based on duration
        if duration == "7_days":
            start_date = now - timedelta(days=7)
        elif duration == "10_days":
            start_date = now - timedelta(days=10)
        elif duration == "current_month":
            start_date = now.replace(day=1)  # First day of the current month
        elif duration == "last_month":
            first_day_of_current_month = now.replace(day=1)
            start_date = (first_day_of_current_month - timedelta(days=1)).replace(day=1)
        elif duration == "last_3_months":
            start_date = now - timedelta(days=90)
            return self._bytes_and_packets_by_month(start_date, now)  # Month-wise data
        else:
            raise ValueError(
                "Invalid duration. Use '7_days', '15_days', '1_month', 'current_month', 'last_month', or 'last_3_months'.")
        # Query the database
        query = (
            self.db.query(
                func.date(NetworkData.created_at).label("date"),  # Group by day
                func.sum(cast(NetworkData.bytes, BigInteger)).label("total_bytes"),
                func.sum(cast(NetworkData.packets, BigInteger)).label("total_packets"),
            )
            .filter(NetworkData.created_at >= start_date, NetworkData.created_at <= now)
            .group_by(func.date(NetworkData.created_at))
            .order_by(func.date(NetworkData.created_at))
        )
        result = query.all()

        # Format the result
        return [
            {
                "date": row.date.strftime("%Y-%m-%d"),
                "total_bytes_gbs": round(self.bytes_to_gb((row.total_bytes)), 2) if row.total_bytes else 0,
                "total_packets": int(row.total_packets) if row.total_packets else 0,
            }
            for row in result
        ]
    def _bytes_and_packets_by_month(self, start_date, end_date):

        query = (
            self.db.query(
                func.date_trunc('month', NetworkData.created_at).label("month"),
                func.sum(cast(NetworkData.bytes, BigInteger)).label("total_bytes"),
                func.sum(cast(NetworkData.packets, BigInteger)).label("total_packets"),
            )
            .filter(NetworkData.created_at >= start_date, NetworkData.created_at <= end_date)
            .group_by(func.date_trunc('month', NetworkData.created_at))
            .order_by(func.date_trunc('month', NetworkData.created_at))
        )
        result = query.all()

        # Convert result into a dictionary
        return [
            {
                "month": row.month.strftime("%Y-%m"),  # Format as YYYY-MM
                "total_bytes_gbs": round(self.bytes_to_gb((row.total_bytes)), 2) if row.total_bytes else 0,
                "total_packets": int(row.total_packets) if row.total_packets else 0,
            }
            for row in result
        ]




    def get_traffic_by_subnet(db, subnet: str):
        # Parse the subnet using ip_network
        subnet_network = ip_network(subnet)

        # Convert the subnet to start and end IPs for SQL filtering
        start_ip = int(subnet_network.network_address)
        end_ip = int(subnet_network.broadcast_address)

        # Query the database for traffic within the subnet range
        query = (
            db.query(
                NetworkData.src_ip,
                NetworkData.dst_ip,
                NetworkData.protocol,
                func.sum(NetworkData.bytes).label("total_bytes"),
                func.count(NetworkData.id).label("packet_count"),
            )
            .filter(
                func.inet_aton(NetworkData.src_ip).between(start_ip, end_ip) |
                func.inet_aton(NetworkData.dst_ip).between(start_ip, end_ip)
            )
            .group_by(NetworkData.src_ip, NetworkData.dst_ip, NetworkData.protocol)
        )

        return query.all()


def get_traffic_by_ports_and_date(db, src_port=None, dst_port=None, start_date=None, end_date=None):
    query = db.query(
        NetworkData.src_port,
        NetworkData.dst_port,
        NetworkData.protocol,
        func.sum(cast(NetworkData.bytes, BigInteger)).label("total_bytes"),
        func.count(NetworkData.id).label("packet_count"),
        func.date(NetworkData.created_at).label("traffic_date"),
    )

    # Apply filters if provided
    if src_port:
        query = query.filter(NetworkData.src_port == src_port)
    if dst_port:
        query = query.filter(NetworkData.dst_port == dst_port)
    if start_date and end_date:
        query = query.filter(NetworkData.created_at.between(start_date, end_date))

    # Group by source port, destination port, and date
    query = query.group_by(NetworkData.src_port, NetworkData.dst_port, func.date(NetworkData.created_at))

    return query.all()
