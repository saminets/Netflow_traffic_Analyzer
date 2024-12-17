from fastapi import APIRouter
from api.v1.nta_collector.routes.nta_collector_routes import router as nta_collector_routes


routers = APIRouter(
    prefix="/nta_collector",
    tags=["nta_collector"],
)

router_list = [
    nta_collector_routes
]

for router in router_list:
    routers.include_router(router)
