from fastapi import APIRouter, Depends, HTTPException
from repository.analytics_repo import Analytics
from schemas.analytics_schema import SrcIpBytes, DestIpBytes,ProtocolStatistics
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
        # import pdb;pdb.set_trace()
        result = analytics.protocol_statisticss()
        return(result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))