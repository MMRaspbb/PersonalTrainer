from ..abstract.base_exercise import BaseExercise
from ..math_engine import calculate_angle
from ..feedback_handler import FeedbackManager
from ..parameters import ParametersManager, ExerciseType
from typing import Tuple, Dict, Any
import time


class SquatCounter(BaseExercise):
    """
    Licznik przysiadów analizujący obie nogi jednocześnie.

    Klasa monitoruje pracę obu nóg, oblicza średni kąt zgięcia kolan
    i generuje informacje zwrotne w czasie rzeczywistym.

    Parametry są pobierane automatycznie z ParametersManager.
    """

    def __init__(self):
        """Inicjalizuje licznik przysiadów z parametrami z ParametersManager"""
        super().__init__(exercise_type=ExerciseType.SQUAT)

        self.fm = FeedbackManager()
        self.feedback = self.fm.get("squat", "start")
        self.avg_angle = 0.0
        self.angle_l = 0.0
        self.angle_r = 0.0
        self._legs_hidden_warned = False

        params = ParametersManager.get_parameters(ExerciseType.SQUAT)
        self._feedback_cooldown = params.feedback.cooldown_seconds
        self._last_feedback_time = 0.0
        self._last_feedback_message = ""

        self._min_angle_variance = ParametersManager.get_custom_param(
            ExerciseType.SQUAT, "min_angle_variance", 5.0
        )
        self._stability_frames = ParametersManager.get_custom_param(
            ExerciseType.SQUAT, "stability_frames", 3
        )

    def _validate_points(self, points: Dict[str, Any]) -> Tuple[bool, str]:
        """Waliduje dostępność i kompletność danych punktów"""
        required_keys = ['l_hip', 'l_knee', 'l_ankle', 'r_hip', 'r_knee', 'r_ankle']
        for key in required_keys:
            if key not in points or points[key] is None:
                return False, "Ustaw się bokiem (widać obie nogi)"
        return True, ""

    def _check_legs_visibility(self, points: Dict[str, Any]) -> bool:
        """Sprawdza czy nogi są widoczne"""
        required_keys = ['l_hip', 'l_knee', 'l_ankle', 'r_hip', 'r_knee', 'r_ankle']
        return all(key in points and points[key] is not None for key in required_keys)

    def _extract_leg_points(self, points: Dict[str, Any]) -> Tuple[list, list]:
        """Ekstrahuje współrzędne (x, y) z punktów anatomicznych"""
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
        """Oblicza kąty zgięcia kolan dla obu nóg"""
        angle_l = calculate_angle(l_pts[0], l_pts[1], l_pts[2])
        angle_r = calculate_angle(r_pts[0], r_pts[1], r_pts[2])
        return angle_l, angle_r, (angle_l + angle_r) / 2

    def _update_state(self, avg_angle: float, is_legs_visible: bool) -> None:
        """Aktualizuje stan maszyny stanowej i feedback na podstawie kąta"""
        if avg_angle > self.threshold_up:
            if self.stage == "down":
                self.counter += 1
                self.feedback = self.fm.get("squat", "good_rep")
            self.stage = "up"
        elif avg_angle < self.threshold_down:
            if self.stage == "up":
                self.feedback = self.fm.get("squat", "go_up")
            self.stage = "down"
        else:
            if self.stage == "up":
                self.feedback = self.fm.get("squat", "go_lower")
            elif self.stage == "down":
                self.feedback = self.fm.get("squat", "extend_fully")

    def _apply_feedback_cooldown(self, current_time: float) -> str:
        """
        Zastosuj cooldown dla feedback'u.

        ZAWSZE zwraca wiadomość aby uniknąć migotania UI.
        Wiadomość zmienia się tylko jeśli zmieniła się OR upłynął cooldown.
        """
        if (self.feedback != self._last_feedback_message or
            current_time - self._last_feedback_time >= self._feedback_cooldown):
            self._last_feedback_message = self.feedback
            self._last_feedback_time = current_time

        return self._last_feedback_message

    def update(self, points: Dict[str, Any]) -> Tuple[int, str, float, str]:
        """Aktualizuje stan licznika na podstawie nowych współrzędnych punktów"""
        is_valid, error_msg = self._validate_points(points)
        if not is_valid:
            return self.counter, self.stage, 0.0, error_msg

        is_legs_visible = self._check_legs_visibility(points)
        l_pts, r_pts = self._extract_leg_points(points)
        self.angle_l, self.angle_r, self.avg_angle = self._calculate_angles(l_pts, r_pts)

        self._update_state(self.avg_angle, is_legs_visible)

        if not is_legs_visible and self.feedback != "Ustaw się bokiem (widać obie nogi)":
            if not self._legs_hidden_warned:
                self.feedback = "Pokaż całe nogi!"
                self._legs_hidden_warned = True

        current_time = time.time()
        feedback_to_return = self._apply_feedback_cooldown(current_time)

        return self.counter, self.stage, self.avg_angle, feedback_to_return

