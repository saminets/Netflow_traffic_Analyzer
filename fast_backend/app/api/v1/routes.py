from fastapi import APIRouter

# from app.api.v1.atom.atom_base_router import routers as atom_router
# from app.api.v1.auto_discovery.auto_discovery_dashboard_routes import \
    # router as auto_discovery_dashboard_router
# from app.api.v1.auto_discovery.auto_discovery_routes import router as auto_discovery_router
# from app.api.v1.monitoring.monitoring_base_router import routers as monitoring_routers
# from app.api.v1.ncm.ncm_base_router import routers as ncm_router
# from app.api.v1.uam.uam_base_router import routers as uam_router
# from app.api.v1.migrations import routers as migration_router
# from app.api.v1.ipam.ipam_base_routes import routers as ipam_router
# from app.api.v1.users.user_base_router import routers as user_router
# from app.api.v1.main.routes.main_dashboard_routes import router as main_dashboard_router
# from app.api.v1.cloud_monitoring.cloud_monitoring_base_router import routers as cloud_monitoring_router
# from app.api.v1.fire_base.fire_base_router import routers as firebase_router
# from app.api.v1.common_routes.common_base_router import routers as common_base_router
# from app.api.v1.data_endpoint.dumy_data_base_router import routers as dummy_data_base_router



### NTA SNMP COLLECTPR SUPPORT
from api.v1.nta_collector.nta_routes import nta_collector_routes as nta_collector_routes



routers = APIRouter()

router_list = [
    # atom_router,
    # auto_discovery_router,
    # auto_discovery_dashboard_router,
    # uam_router,
    # monitoring_routers,
    # ncm_router,
    # migration_router,
    # ipam_router,
    # user_router,
    # main_dashboard_router,
    # cloud_monitoring_router,
    # firebase_router,
    # common_base_router,
    # dummy_data_base_router,
    nta_collector_routes,  # NTA SNMP COLLECTOR SUPPORT

]

for router in router_list:
    routers.include_router(router)
