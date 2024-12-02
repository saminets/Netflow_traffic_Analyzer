from datetime import datetime
from ipaddress import ip_network
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from repository.analytics_repo import Analytics
from schemas.analytics_schema import (SrcIpBytes, DestIpBytes,
                                      ProtocolStatistics,HourlyStatistics,Srcport,Destport,TrafficData,TrafficQueryParams)

from schemas.analytics_schema import SrcIpBytes, DestIpBytes, ProtocolStatistics, TrafficResponse
from core.dependencies import get_analytics

analytics_router = APIRouter()

@analytics_router.get("/top-traffic-sources", response_model=list[SrcIpBytes])
def get_top_traffic_sources(
    limit: int = 10, analytics: Analytics = Depends(get_analytics)
):
    try:
        result = analytics.top_10_sources(limit=limit)
        print("Top 10 sources",result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@analytics_router.get("/top-traffic-destinations", response_model=list[DestIpBytes])
def get_top_traffic_destinations(
    limit: int = 10, analytics: Analytics = Depends(get_analytics)
):

    try:
        result = analytics.top_10_destinations(limit=limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@analytics_router.get("/protocol-statistics", response_model=list[ProtocolStatistics])
def get_protocol_statistics(analytics: Analytics = Depends(get_analytics)):

    try:
        result = analytics.protocol_statisticss()
        return(result)
        return result
    except Exception as e:
        import traceback;traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@analytics_router.get("/traffic-to-port/{port}", response_model=list[TrafficResponse])
def get_traffic_to_port(port: str, analytics: Analytics = Depends(get_analytics)):
    try:
        result = analytics.get_traffic_to_port(port)
        print("-------------",result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@analytics_router.get("/hourly-statistics", response_model=list[HourlyStatistics])
def get_hourly_statistics(analytics: Analytics = Depends(get_analytics)):

    try:
        result = analytics.hourly_statistics()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@analytics_router.get("/top_source_port", response_model=list[Srcport])
def get_source_port( limit: int = 10,analytics: Analytics = Depends(get_analytics)):
    try:
        result = analytics.top_10_sourcesport(limit=limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@analytics_router.get("/top_destinaton_port", response_model=list[Destport])
def get_source_port( limit: int = 10,analytics: Analytics = Depends(get_analytics)):
    try:
        result = analytics.top_10_destinationport(limit=limit)
        print(result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@analytics_router.get("/bytes-and-packets")
def get_bytes_and_packets(duration: str, analytics: Analytics = Depends(get_analytics)):
    try:
        result = analytics.bytes_and_packets_by_duration(duration)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


# Traffic search by subnet API
@analytics_router.get("/traffic-by-subnet", response_model=List[TrafficData])
def get_traffic(subnet: str,analytics: Analytics = Depends(get_analytics)):
    # Validate the subnet
    try:
        ip_network(subnet)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid subnet")

    # Fetch traffic data
    traffic_data = analytics.get_traffic_by_subnet(subnet)
    if not traffic_data:
        raise HTTPException(status_code=404, detail="No traffic found for the subnet")

    # Convert to response model
    response = [
        TrafficData(
            src_ip=row.src_ip,
            dst_ip=row.dst_ip,
            protocol=row.protocol,
            total_bytes=row.total_bytes,
            packet_count=row.packet_count,
        )
        for row in traffic_data
    ]
    return response

@analytics_router.get("/traffic", response_model=List[TrafficData])
def get_traffic(params: TrafficQueryParams = Depends(), analytics: Analytics = Depends(get_analytics)):
    # Validate date format (already enforced by Pydantic regex)
    try:
        start_date_dt = datetime.strptime(params.start_date, "%Y-%m-%d") if params.start_date else None
        end_date_dt = datetime.strptime(params.end_date, "%Y-%m-%d") if params.end_date else None
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    # Fetch traffic data
    traffic_data = analytics.get_traffic_by_ports_and_date(
        src_port=params.src_port,
        dst_port=params.dst_port,
        start_date=start_date_dt,

        end_date=end_date_dt
    )

    if not traffic_data:
        raise HTTPException(status_code=404, detail="No traffic data found")

    return [
        TrafficData(
            src_port=row.src_port,
            dst_port=row.dst_port,
            protocol=row.protocol,
            total_bytes=row.total_bytes,
            packet_count=row.packet_count,
            traffic_date=str(row.traffic_date),
        )
        for row in traffic_data
    ]