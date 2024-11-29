from pydantic import BaseModel


class SrcIpBytes(BaseModel):
    src_ip: str
    total_bytes_gbs: float

class DestIpBytes(BaseModel):
    dest_ip: str
    total_bytes_gbs: float
class ProtocolStatistics(BaseModel):
    protocol: str
    total_flows: int
    total_bytes_gbs: float
    total_packets: int