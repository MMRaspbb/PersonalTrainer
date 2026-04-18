import httpx
from fastapi import FastAPI
from contextlib import asynccontextmanager


# Symulacja importu od Osoby 1 (AI)
# from app.services.vision_engine import MediaPipeEngine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- SEKCJA STARTUP (Przygotowanie) ---

    # 1. Inicjalizacja MediaPipe (Osoba 1)
    # Ładujemy framework raz, by był "rozgrzany" i gotowy na binarkę z WebSocketu.
    # app.state.pose_engine = MediaPipeEngine()
    print("INFO: MediaPipe zainicjalizowany. Gotowy na odbiór klatek binarnych.")

    # 2. Inicjalizacja klienta do komunikacji z Javą (Twoje zadanie)
    # Tworzymy jeden wspólny klient HTTP, żeby nie otwierać nowego połączenia
    # przy każdym raporcie końcowym (oszczędność czasu i zasobów).
    app.state.java_client = httpx.AsyncClient(
        base_url="http://twoja-java-api.com",
        timeout=5.0
    )
    print("INFO: Klient HTTP dla serwera Java gotowy.")

    # 3. Cache dla ExerciseDB (Opcjonalnie)
    # Możesz tu zainicjalizować serwis, który trzyma linki do GIFów w pamięci.
    print("INFO: System instruktażu ExerciseDB aktywny.")

    yield  # W tym momencie rusza serwer i WebSockety zaczynają pompować dane

    # --- SEKCJA SHUTDOWN (Sprzątanie) ---

    # Zamykamy połączenie z Javą i zwalniamy pamięć po MediaPipe
    await app.state.java_client.aclose()
    # app.state.pose_engine.release()
    print("INFO: Zasoby zwolnione. Serwer wyłączony poprawnie.")