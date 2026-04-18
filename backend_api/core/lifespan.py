import httpx
from fastapi import FastAPI
from contextlib import asynccontextmanager

# Import od Osoby 1 (AI) - klasa detektora
from model.logic.pose_detector import PoseDetector

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- SEKCJA STARTUP (Przygotowanie) ---

    # 1. Inicjalizacja MediaPipe (Osoba 1)
    # Ścieżka do modelu dostarczonego przez Osobę 1
    model_path = "model/tasks/pose_landmarker_full.task"
    app.state.pose_engine = PoseDetector(model_path)
    print("INFO: MediaPipe zainicjalizowany. Gotowy na odbiór klatek binarnych.")

    # 2. Inicjalizacja klienta do komunikacji z Javą (Twoje zadanie)
    # Używamy wspólnego klienta HTTP dla wydajności raportowania końcowego.
    app.state.java_client = httpx.AsyncClient(
        base_url="http://twoja-java-api.com",
        timeout=5.0
    )
    print("INFO: Klient HTTP dla serwera Java gotowy.")

    # 3. Cache dla ExerciseDB (Opcjonalnie)
    print("INFO: System instruktażu ExerciseDB aktywny.")

    yield  # W tym momencie rusza serwer i WebSockety zaczynają przyjmować dane

    # --- SEKCJA SHUTDOWN (Sprzątanie) ---

    # Zamykamy połączenie z Javą i zwalniamy pamięć modelu
    await app.state.java_client.aclose()
    app.state.pose_engine.close()
    print("INFO: Zasoby zwolnione. Serwer wyłączony poprawnie.")