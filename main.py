from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend_api.api import websockets
from backend_api.core import lifespan
app = FastAPI(
    title="Real-Time Video Analytics Engine",
    lifespan=lifespan # Tutaj Osoba 1 załaduje model MediaPipe
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Podłączamy tylko router WebSocketów, bo to serce Twojej części
app.include_router(websockets.router)

@app.get("/health")
async def health_check():
    return {"status": "ready", "engine": "numpy_biomechanics"}