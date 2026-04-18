import mediapipe as mp
import cv2
import time
import numpy as np
import asyncio
import websockets
import json

from model.visual import Visual


class StreamServer:
    """Zarządza połączeniami przychodzącymi, odbiera klatki i odsyła JSON-y."""

    def __init__(self, detector: PoseDetector, host="0.0.0.0", port=8765):
        self.detector = detector
        self.host = host
        self.port = port

    async def handle_client(self, websocket):  # Usunięto 'path' w sygnaturze dla nowszych wersji
        print(f"Nowe połączenie: {websocket.remote_address}")
        start_time = time.time()

        try:
            # Pętla nasłuchująca na wiadomości od klienta (aplikacji na telefonie)
            async for message in websocket:
                # Zakładamy, że klient wysyła skompresowaną klatkę wideo (bajty JPEG)
                # Konwertujemy bajty sieciowe na obraz zrozumiały dla OpenCV
                nparr = np.frombuffer(message, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if frame is None:
                    continue

                h, w, _ = frame.shape

                # MediaPipe wymaga rosnącego znacznika czasu w trybie VIDEO
                timestamp_ms = int((time.time() - start_time) * 1000)

                # 1. AI analizuje obraz
                result = self.detector.detect(frame, timestamp_ms)

                # 2. Przygotowanie paczki z danymi (JSON)
                response_data = {"status": "no_pose", "points": {}}

                if result.pose_landmarks:
                    # Jeśli AI kogoś widzi, wyciągamy punkty z pierwszej wykrytej osoby [0]
                    extracted_points = Visual.get_key_points(result.pose_landmarks[0], w, h)
                    response_data = {
                        "status": "success",
                        "points": extracted_points
                    }

                # 3. Natychmiastowe odesłanie punktów do aplikacji w formacie JSON
                await websocket.send(json.dumps(response_data))

        except websockets.exceptions.ConnectionClosed:
            print(f"Klient {websocket.remote_address} rozłączył się.")
        except Exception as e:
            print(f"Błąd połączenia: {e}")

    async def start(self):
        print(f"Uruchamiam serwer SmartForm AI na ws://{self.host}:{self.port}")
        # Uruchomienie serwera WebSocket
        async with websockets.serve(self.handle_client, self.host, self.port):
            await asyncio.Future()  # Pętla działa w nieskończoność


# ==========================================
# PUNKT STARTOWY
# ==========================================
if __name__ == "__main__":
    MODEL_PATH = '/model/tasks/pose_landmarker_full.task'

    detector = PoseDetector(MODEL_PATH)
    server = StreamServer(detector, host="127.0.0.0", port=8765)  # 127.0.0.1 dla testów lokalnych

    # asyncio.run uruchamia asynchroniczną pętlę serwera
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("Wyłączanie serwera...")
        detector.close()