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
        Główna metoda procesująca klatkę obrazu z dodatkową walidacją.
        """
        # 1. Zarządzanie instancją ćwiczenia (Lazy Loading)
        if not exercise_type:
            return ExerciseResponse(counter=0, stage="unknown", message="Brak typu ćwiczenia", angle=0.0)

        if self._current_type != exercise_type.lower():
            try:
                self._current_exercise = ExerciseFactory.get_exercise(exercise_type)
                self._current_type = exercise_type.lower()
            except ValueError as e:
                return ExerciseResponse(counter=0, stage="error", message=str(e), angle=0.0)

        # 2. Detekcja AI
        result = self.detector.detect(frame, frame_ms)

        # DODANE SPRAWDZENIE: Czy postać została wykryta
        if not result or not result.pose_landmarks:
            # Sprawdzenie, czy self._current_exercise nie jest nullem przed dostępem do atrybutów
            current_counter = self._current_exercise.counter if self._current_exercise else 0
            current_stage = self._current_exercise.stage if self._current_exercise else "unknown"

            return ExerciseResponse(
                counter=current_counter,
                stage=current_stage,
                message="Nie wykryto postaci",
                angle=0.0
            )

        # 3. Translacja na współrzędne robocze
        h, w, _ = frame.shape
        points = Translator.get_key_points(result.pose_landmarks[0], w, h)

        # 4. Wykonanie logiki ćwiczenia (z zabezpieczeniem przed nullem)
        if self._current_exercise:
            counter, stage, angle, message = self._current_exercise.update(points)
        else:
            return ExerciseResponse(counter=0, stage="error", message="Błąd inicjalizacji ćwiczenia", angle=0.0)

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