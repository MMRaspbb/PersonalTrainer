from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# 1. IMPORTUJ TWOJE ROUTERY
from backend_api.api import websockets, rest_endpoints
from backend_api.core.lifespan import lifespan

app = FastAPI(
    title="Real-Time Video Analytics Engine",
    lifespan=lifespan
)

# CORS (ważne dla Reacta)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. ZAREJESTRUJ ROUTERY (To wypełni Swaggera)
app.include_router(rest_endpoints.router, prefix="/api")
app.include_router(websockets.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)