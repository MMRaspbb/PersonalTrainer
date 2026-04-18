from ..abstract.base_exercise import BaseExercise
from ..math_engine import calculate_angle
from ..feedback_handler import FeedbackManager
from typing import Tuple, Dict, Any

class SquatCounter(BaseExercise):
    """
    Licznik przysiadów analizujący obie nogi jednocześnie.

    Klasa monitoruje pracę obu nóg, oblicza średni kąt zgięcia kolan
    i generuje informacje zwrotne w czasie rzeczywistym.
    """

    def __init__(self):
        """Inicjalizuje licznik przysiadów z progami dla różnych faz ruchu."""
        super().__init__(threshold_down=90.0, threshold_up=160.0)
        self.fm = FeedbackManager()
        self.feedback = self.fm.get("squat", "start")
        self.avg_angle = 0.0
        self.angle_l = 0.0
        self.angle_r = 0.0

    def _validate_points(self, points: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Waliduje dostępność i kompletność danych punktów.

        Args:
            points: Słownik ze współrzędnymi punktów anatomicznych

        Returns:
            Krotka (czy_dane_są_poprawne, komunikat_błędu)
        """
        required_keys = ['l_hip', 'l_knee', 'l_ankle', 'r_hip', 'r_knee', 'r_ankle']

        for key in required_keys:
            if key not in points or points[key] is None:
                return False, "Ustaw się bokiem (widać obie nogi)"

        return True, ""

    def _extract_leg_points(self, points: Dict[str, Any]) -> Tuple[list, list]:
        """
        Ekstrahuje współrzędne (x, y) z punktów anatomicznych dla obu nóg.

        Args:
            points: Słownik ze współrzędnymi punktów

        Returns:
            Krotka z listami współrzędnych dla lewej i prawej nogi
        """
        l_pts = [
            (points['l_hip']['x'], points['l_hip']['y']),
            (points['l_knee']['x'], points['l_knee']['y']),
            (points['l_ankle']['x'], points['l_ankle']['y'])
        ]
        r_pts = [
            (points['r_hip']['x'], points['r_hip']['y']),
            (points['r_knee']['x'], points['r_knee']['y']),
            (points['r_ankle']['x'], points['r_ankle']['y'])
        ]
        return l_pts, r_pts

    def _calculate_angles(self, l_pts: list, r_pts: list) -> Tuple[float, float, float]:
        """
        Oblicza kąty zgięcia kolan dla obu nóg i wartość średnią.

        Args:
            l_pts: Lista współrzędnych lewej nogi [hip, knee, ankle]
            r_pts: Lista współrzędnych prawej nogi [hip, knee, ankle]

        Returns:
            Krotka (kąt_lewy, kąt_prawy, kąt_średni)
        """
        angle_l = calculate_angle(l_pts[0], l_pts[1], l_pts[2])
        angle_r = calculate_angle(r_pts[0], r_pts[1], r_pts[2])
        avg_angle = (angle_l + angle_r) / 2

        return angle_l, angle_r, avg_angle

    def _update_state(self, avg_angle: float) -> None:
        """
        Aktualizuje stan maszyny stanowej i feedback na podstawie kąta.

        Args:
            avg_angle: Średni kąt zgięcia kolan
        """
        if avg_angle > self.threshold_up:
            # Faza pełnego wyprostu
            if self.stage == "down":
                self.counter += 1
                self.feedback = self.fm.get("squat", "good_rep")
            self.stage = "up"

        elif avg_angle < self.threshold_down:
            # Faza pełnego zgięcia
            if self.stage == "up":
                self.feedback = self.fm.get("squat", "go_up")
            self.stage = "down"

        else:
            # Faza pośrednia - feedback motywacyjny
            if self.stage == "up":
                self.feedback = self.fm.get("squat", "go_lower")
            elif self.stage == "down":
                self.feedback = self.fm.get("squat", "extend_fully")

    def update(self, points: Dict[str, Any]) -> Tuple[int, str, float, str]:
        """
        Aktualizuje stan licznika na podstawie nowych współrzędnych punktów.

        Args:
            points: Słownik ze współrzędnymi punktów anatomicznych w formacie:
                   {'l_hip': {'x': float, 'y': float}, ...}

        Returns:
            Krotka (licznik, stan, średni_kąt, komunikat_feedback)
        """
        # Walidacja danych wejściowych
        is_valid, error_msg = self._validate_points(points)
        if not is_valid:
            return self.counter, self.stage, 0.0, error_msg

        # Ekstrahowanie punktów
        l_pts, r_pts = self._extract_leg_points(points)

        # Obliczenie kątów
        self.angle_l, self.angle_r, self.avg_angle = self._calculate_angles(l_pts, r_pts)

        # Aktualizacja stanu
        self._update_state(self.avg_angle)

        return self.counter, self.stage, self.avg_angle, self.feedback
