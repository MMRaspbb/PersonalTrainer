import time

import numpy as np
from typing import Dict, Optional, Any
import cv2

from model.logic.pose_detector import PoseDetector
from model.logic.renderer import Renderer
from model.logic.translator import Translator


class PoseController:
    """Kontroler orkiestrujący proces detekcji AI i translacji danych na współrzędne."""

    def __init__(self, detector: PoseDetector) -> None:
        """
        Przyjmuje zainicjalizowany obiekt PoseDetector.
        """
        self.detector = detector

    def process_frame(self, frame: np.ndarray, timestamp_ms: int) -> Dict[str, Optional[Dict[str, int]]]:
        """
        Główna metoda kontrolera. Otrzymuje klatkę wideo, zleca analizę do AI,
        a następnie używa Translatora do zwrotu gotowego słownika z punktami.
        """
        h: int
        w: int
        h, w, _ = frame.shape

        result = self.detector.detect(frame, timestamp_ms)

        if result and result.pose_landmarks:
            return Translator.get_key_points(result.pose_landmarks[0], w, h)

        return {}


if __name__ == "__main__":
    MODEL_PATH = '/Users/vecnine/Desktop/programowanie/python projects/PersonalTrainer/model/tasks/pose_landmarker_full.task'

    detector = PoseDetector(MODEL_PATH)
    cap = cv2.VideoCapture(0)

    start_time = time.time()

    print("Wciśnij 'q' aby zamknąć okno.")

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)

        timestamp_ms = int((time.time() - start_time) * 1000)

        result = detector.detect(frame, timestamp_ms)

        if result and result.pose_landmarks:
            Renderer.draw(frame, result.pose_landmarks[0])

        cv2.imshow('Podglad Debug', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    detector.close()