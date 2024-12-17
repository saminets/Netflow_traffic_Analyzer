import sys


import time
import sys
import traceback
import uvicorn
import asyncio
from fastapi import FastAPI,Request,HTTPException,Depends
from starlette.middleware.cors import CORSMiddleware
import uuid
# Import Routes
from api.v1.routes import routers as v1_routers
# from app.api.v2.routes import routers as v2_routers
# Import Database and Models
# Import Container and Configs

#Middleware
# from app.middleware import AuthMiddleware
from fastapi.openapi.docs import get_swagger_ui_oauth2_redirect_html


# Initialize FastAPI app
app = FastAPI(title="MonetX_2.0", openapi_url=f"/api/openapi.json", version="0.0.1")

#
# app.add_middleware(DatabaseManager)
# logger.info("DatabaseMiddleware added to FastAPI app.")
# app.middleware("http")(AuthMiddleware())

app.include_router(v1_routers, prefix="/api/v1")

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True, debug=True, loop="asyncio")











