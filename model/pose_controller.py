import time
import cv2
import os
import numpy as np
from typing import Optional

# Importy logiki detekcji i renderowania
from logic.pose_detector import PoseDetector
from logic.translator import Translator
from logic.renderer import Renderer

# Importy logiki ćwiczeń
from exercise_logic.exercises.squat import SquatCounter
from exercise_logic.exercises.pushup import PushupCounter


class PoseController:
    """
    Główny kontroler aplikacji orkiestrujący przepływ danych:
    Kamera -> AI -> Translator -> Logika Cwiczenia -> Renderer.
    """

    def __init__(self, model_path: str, exercise_type: str = "squat"):
        # Inicjalizacja detektora AI
        self.detector = PoseDetector(model_path)

        # Inicjalizacja wybranego ćwiczenia (Fabryka)
        self.exercise = self._get_exercise_instance(exercise_type)

        # Parametry wideo
        self.cap = cv2.VideoCapture(0)
        self.start_time = time.time()

    def _get_exercise_instance(self, exercise_type: str):
        """Prosta fabryka do wyboru ćwiczenia."""
        exercises = {
            "squat": SquatCounter,
            "pushup": PushupCounter
        }
        exercise_class = exercises.get(exercise_type.lower())
        if not exercise_class:
            raise ValueError(f"Nieznany typ ćwiczenia: {exercise_type}")
        return exercise_class()

    def run(self):
        """Główna pętla uruchamiająca aplikację."""
        print(f"Uruchomiono tryb: {type(self.exercise).__name__}")
        print("Wciśnij 'q', aby wyjść.")

        while self.cap.isOpened():
            success, frame = self.cap.read()
            if not success:
                break

            # Przygotowanie klatki
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            timestamp_ms = int((time.time() - self.start_time) * 1000)

            # 1. Detekcja AI
            result = self.detector.detect(frame, timestamp_ms)

            if result and result.pose_landmarks:
                landmarks = result.pose_landmarks[0]

                # 2. Rysowanie podstawowego szkieletu
                Renderer.draw(frame, landmarks)

                # 3. Translacja wyników na punkty (piksele)
                points = Translator.get_key_points(landmarks, w, h)

                # 4. Aktualizacja logiki ćwiczenia
                # Metoda update przyjmuje cały słownik punktów, co ułatwia zmianę ćwiczenia
                reps, stage, angle, feedback = self.exercise.update(points)

                # 5. Renderowanie nakładki informacyjnej (HUD)
                Renderer.draw_stats(frame, reps, stage, feedback)

                # Opcjonalne: rysowanie kąta przy odpowiednim stawie
                self._draw_dynamic_angle(frame, points, angle)

            # Wyświetlanie obrazu (zawsze, nawet przy braku detekcji)
            cv2.imshow('AI Personal Trainer', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cleanup()

    def _draw_dynamic_angle(self, frame, points, angle):
        """Pomocnicza metoda do rysowania kąta przy kluczowym stawie."""
        if angle <= 0:
            return

        # Wybór stawu do opisu kąta w zależności od ćwiczenia
        target_joint = None
        if isinstance(self.exercise, SquatCounter):
            target_joint = points.get('l_knee')
        elif isinstance(self.exercise, PushupCounter):
            target_joint = points.get('l_elbow')

        if target_joint:
            Renderer.draw_angle(frame, target_joint, angle)

    def cleanup(self):
        """Zwalnianie zasobów."""
        self.cap.release()
        cv2.destroyAllWindows()
        self.detector.close()


if __name__ == "__main__":
    # Ścieżka do modelu AI
    BASE_DIR = os.path.dirname(__file__)
    MODEL_PATH = os.path.join(BASE_DIR, 'tasks/pose_landmarker_full.task')

    # Możesz tutaj łatwo zmienić "squat" na "pushup"
    controller = PoseController(MODEL_PATH, exercise_type="pushup")
    controller.run()