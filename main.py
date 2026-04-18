from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend_api.core.lifespan import lifespan
from backend_api.api.rest_endpoints import router as rest_router
from backend_api.api.websockets import router as ws_router

app = FastAPI(
    title="Real-Time Video Analytics Engine",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ONLY ONCE
app.include_router(rest_router, prefix="/api")
app.include_router(ws_router)