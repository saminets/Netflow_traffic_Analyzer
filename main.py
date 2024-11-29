from fastapi import FastAPI

from core.database import Base, engine
from api.routes.analytics_router import analytics_router
# Create tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include the analytics routes
app.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
