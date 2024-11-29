from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from core.database import Base, engine
from api.routes.analytics_router import analytics_router
# Create tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI()


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with allowed origins, e.g., ["https://example.com"]
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Custom Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Log the request
    print(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    # Log the response status code
    print(f"Response status: {response.status_code}")
    return response
# Include the analytics routes
app.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
