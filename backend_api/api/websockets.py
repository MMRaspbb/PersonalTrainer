import cv2
import numpy as np
import time
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend_api.models.schemas import RealTimeFeedback
from model.math.exercise_logic import SquatCounter  # Import logiki biomechanicznej

router = APIRouter()


@router.websocket("/ws")
async def video_stream_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Połączono z kamerą (React)")

    # 1. Inicjalizacja licznika dla tej sesji (np. przysiady)
    exercise_manager = SquatCounter()

    # 2. Pobranie zainicjalizowanego silnika MediaPipe ze stanu aplikacji
    pose_engine = websocket.app.state.pose_engine

    try:
        while True:
            # 3. Odbiór binarny klatki (Blob JPEG z Reacta)
            data = await websocket.receive_bytes()

            # 4. Dekodowanie bajtów do macierzy pikseli
            nparr = np.frombuffer(data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if frame is None:
                continue

            # 5. PRZEKAZANIE DO MEDIAPIPE
            # Tryb VIDEO wymaga znacznika czasu w milisekundach
            timestamp_ms = int(time.time() * 1000)
            result = pose_engine.detect(frame, timestamp_ms)

            # 6. ANALIZA WYNIKÓW I BIOMECHANIKA
            if result.pose_landmarks:
                print(result.pose_landmarks[0])
                # Wyciągamy punkty dla pierwszego wykrytego szkieletu
                # landmarks = result.pose_landmarks[0]
                #
                # # Pobieramy współrzędne (x, y) dla stawów: biodro(24), kolano(26), kostka(28)
                # hip = [landmarks[24].x, landmarks[24].y]
                # knee = [landmarks[26].x, landmarks[26].y]
                # ankle = [landmarks[28].x, landmarks[28].y]
                #
                # # Aktualizujemy licznik powtórzeń
                # count, stage, angle,feedback = exercise_manager.update(hip, knee, ankle)
                #
                # # Przygotowujemy prawdziwy feedback
                # response = RealTimeFeedback(
                #     is_tracking=True,
                #     rep_count=count,
                #     feedback = feedback
                # )
            else:
                print("gowno")
                # response = RealTimeFeedback(
                #     is_tracking=False,
                #     rep_count=exercise_manager.counter,
                #     feedback = "Błąd obrazu"
                # )

            # 7. WYSYŁKA JSON Z WYNIKAMI DO REACTA
            # await websocket.send_json(response.dict())

    except WebSocketDisconnect:
        print("Kamera rozłączona. Sesja zakończona.")
        # Tutaj możesz wysłać końcowy raport do Javy używając app.state.java_client