from typing import Optional

from pydantic import BaseModel,Field
class TrafficData(BaseModel):
    src_ip: str
    dst_ip: str
    protocol: str
    total_bytes: int
    packet_count: int

class SrcIpBytes(BaseModel):
    src_ip:  Optional[str]
    total_bytes_gbs: float

class DestIpBytes(BaseModel):
    dest_ip:  Optional[str]
    total_bytes_gbs: float
class ProtocolStatistics(BaseModel):
    protocol:  Optional[str]
    total_flows: int
    total_bytes_gbs: float
    total_packets: int

class HourlyStatistics(BaseModel):
    hour: str  # Timestamp of the hour
    total_bytes_gbs: float  # Total bytes converted to gigabytes
    total_packets: int  # Total packets
class Destport(BaseModel):
    destination_port:  Optional[str]
    total_bytes_gbs: float
class Srcport(BaseModel):
    source_port:  Optional[str]
    total_bytes_gbs: float
class TrafficData(BaseModel):
    src_port: Optional[int]
    dst_port: Optional[int]
    protocol: str
    total_bytes: float
    packet_count: int
    traffic_date: str
class TrafficQueryParams(BaseModel):
    src_port: Optional[int]
    dst_port: Optional[int]
    start_date: Optional[str]
    end_date: Optional[str]