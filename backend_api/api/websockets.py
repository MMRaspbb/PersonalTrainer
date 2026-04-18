import cv2
import numpy as np
import time
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from numpy.ma.core import angle

from backend_api.models.schemas import RealTimeFeedback
from model.exercise_logic.exercise_logic import SquatCounter  # Import logiki biomechanicznej
from model.exercise_handler import ExerciseHandler

router = APIRouter()


@router.websocket("/ws")
async def video_stream_endpoint(websocket: WebSocket):
    await websocket.accept()
#     print("Połączono z kamerą (React)")

    # 1. Inicjalizacja licznika dla tej sesji (np. przysiady)
    exercise_manager = ExerciseHandler("model/tasks/pose_landmarker_full.task")

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
            result = exercise_manager.process(frame, timestamp_ms,"squat")

            # 6. ANALIZA WYNIKÓW I BIOMECHANIKA
            if result.message != "Nie wykryto postaci":
                print("dziala")
                # Przygotowujemy prawdziwy feedback
                response = RealTimeFeedback(
                    is_tracking=True,
                    rep_count=result.counter,
                    angle = result.counter,
                    feedback = result.message

                )
            else:
                print("gowno")
                response = RealTimeFeedback(
                    is_tracking=False,
                    rep_count=result.counter,
                    angle = result.counter,
                    feedback = result.message
                )

            # 7. WYSYŁKA JSON Z WYNIKAMI DO REACTA
            print(response.dict())
            await websocket.send_json(response.dict())

    except WebSocketDisconnect:
        print("Kamera rozłączona. Sesja zakończona.")
        # Tutaj możesz wysłać końcowy raport do Javy używając app.state.java_client