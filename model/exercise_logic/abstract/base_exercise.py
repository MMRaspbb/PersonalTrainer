from abc import ABC, abstractmethod
from typing import Optional
from ..parameters import ParametersManager, ExerciseType

class BaseExercise(ABC):
    """
    Abstrakcyjna klasa bazowa dla wszystkich ćwiczeń.

    Automatycznie pobiera parametry z ParametersManager.
    Umożliwia łatwą konfigurację bez modyfikowania kodu logiki.
    """

    def __init__(self, threshold_down: Optional[float] = None,
                 threshold_up: Optional[float] = None,
                 exercise_type: Optional[ExerciseType] = None):
        """
        Inicjalizacja ćwiczenia.

        Args:
            threshold_down: Próg dolny (jeśli None, pobierz z ParametersManager)
            threshold_up: Próg górny (jeśli None, pobierz z ParametersManager)
            exercise_type: Typ ćwiczenia dla ParametersManager
        """
        self.counter = 0
        self.stage = "up"
        self.exercise_type = exercise_type

        # Jeśli dostarczono progi, użyj ich, inaczej pobierz z ParametersManager
        if threshold_down is not None and threshold_up is not None:
            self.threshold_down = threshold_down
            self.threshold_up = threshold_up
        elif exercise_type is not None:
            # Pobierz z ParametersManager
            self.threshold_down = ParametersManager.get_threshold_down(exercise_type)
            self.threshold_up = ParametersManager.get_threshold_up(exercise_type)
        else:
            # Fallback na domyślne wartości
            self.threshold_down = 90.0
            self.threshold_up = 160.0

    def _process_state(self, current_angle):
        rep_completed = False
        if current_angle < self.threshold_down:
            self.stage = "down"
        if current_angle > self.threshold_up and self.stage == "down":
            self.stage = "up"
            rep_completed = True
        return rep_completed

    @abstractmethod
    def update(self, points):
        """Metoda przyjmuje słownik punktów i zwraca (counter, stage, angle, feedback)."""
        pass