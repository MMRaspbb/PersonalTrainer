import numpy as np
from typing import Dict, Optional

# Importy komponentów technicznych
from .logic.pose_detector import PoseDetector
from .logic.translator import Translator
from .exercise_logic.exercise_factory import ExerciseFactory
from .structs.exercise_response import ExerciseResponse


class ExerciseHandler:
    """
    Wysokopoziomowa fasada (Facade) do analizy ćwiczeń.
    Ukrywa detale detekcji AI i translacji danych.
    """

    def __init__(self, model_path: str):
        """
        Inicjalizuje silnik AI.
        Handler jest właścicielem detektora, co ułatwia zarządzanie zasobami.
        """
        self.detector = PoseDetector(model_path)
        self._current_exercise = None
        self._current_type = ""

    def process(self, frame: np.ndarray, frame_ms: int, exercise_type: str) -> ExerciseResponse:
        """
        Główna metoda procesująca klatkę obrazu.

        Args:
            frame: Obraz z kamery (BGR/RGB).
            frame_ms: Timestamp klatki w milisekundach.
            exercise_type: Nazwa ćwiczenia (np. 'squat', 'pushup').

        Returns:
            ExerciseResponse: Ustandaryzowany obiekt z wynikiem.
        """
        # 1. Zarządzanie instancją ćwiczenia (Lazy Loading + Caching)
        # Dzięki temu licznik nie zeruje się przy każdej klatce
        if self._current_type != exercise_type.lower():
            self._current_exercise = ExerciseFactory.get_exercise(exercise_type)
            self._current_type = exercise_type.lower()

        # 2. Detekcja AI
        # Wykorzystujemy dedykowany moduł detekcji
        result = self.detector.detect(frame, frame_ms)

        if not result or not result.pose_landmarks:
            return ExerciseResponse(
                counter=self._current_exercise.counter,
                stage=self._current_exercise.stage,
                message="Nie wykryto postaci",
                angle=0.0
            )

        # 3. Translacja na współrzędne robocze
        # Zamieniamy surowe dane AI na czytelny słownik punktów
        h, w, _ = frame.shape
        points = Translator.get_key_points(result.pose_landmarks[0], w, h)

        # 4. Wykonanie logiki ćwiczenia
        # Każde ćwiczenie implementuje ten sam interfejs update(points)
        counter, stage, angle, message = self._current_exercise.update(points)

        # 5. Zwrócenie ustandaryzowanego wyniku
        return ExerciseResponse(
            counter=counter,
            stage=stage,
            message=message,
            angle=angle
        )

    def close(self):
        """Bezpieczne zamknięcie detektora."""
        self.detector.close()