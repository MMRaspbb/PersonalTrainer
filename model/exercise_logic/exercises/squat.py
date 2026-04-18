from ..abstract.base_exercise import BaseExercise
from ..math_engine import calculate_angle
from ..feedback_handler import FeedbackManager
from typing import Tuple, Dict, Any
import time

from ..parameters import ExerciseType


class SquatCounter(BaseExercise):
    def __init__(self):
        super().__init__(exercise_type=ExerciseType.SQUAT)
        self.fm = FeedbackManager()
        self.feedback = self.fm.get("squat", "start")
        self._current_event = "start"  # Śledzimy kategorię zdarzenia
        self._last_feedback_time = 0.0
        self._last_displayed_message = self.feedback
        self._feedback_cooldown = 1.5  # Czas wyświetlania jednej wiadomości

    def _update_state(self, avg_angle: float, is_legs_visible: bool) -> None:
        """Wybiera nowe zdarzenie tylko, gdy nastąpiła zmiana logiczna."""
        new_event = self._current_event

        if avg_angle > self.threshold_up:
            if self.stage == "down":
                self.counter += 1
                new_event = "good_rep"
            self.stage = "up"
        elif avg_angle < self.threshold_down:
            if self.stage == "up":
                new_event = "go_up"
            self.stage = "down"
        else:
            if self.stage == "up":
                new_event = "go_lower"
            elif self.stage == "down":
                new_event = "extend_fully"

        # Losujemy nową wiadomość TYLKO jeśli zmienił się typ zdarzenia
        if new_event != self._current_event:
            self._current_event = new_event
            self.feedback = self.fm.get("squat", new_event)

    def update(self, points: Dict[str, Any]) -> Tuple[int, str, float, str]:
        required = ['l_hip', 'l_knee', 'l_ankle', 'r_hip', 'r_knee', 'r_ankle']
        if not all(k in points and points[k] is not None for k in required):
            return self.counter, self.stage, 0.0, "Ustaw się bokiem (pokaż nogi)"

        l_pts = [(points['l_hip']['x'], points['l_hip']['y']), (points['l_knee']['x'], points['l_knee']['y']),
                 (points['l_ankle']['x'], points['l_ankle']['y'])]
        r_pts = [(points['r_hip']['x'], points['r_hip']['y']), (points['r_knee']['x'], points['r_knee']['y']),
                 (points['r_ankle']['x'], points['r_ankle']['y'])]

        angle_l = calculate_angle(l_pts[0], l_pts[1], l_pts[2])
        angle_r = calculate_angle(r_pts[0], r_pts[1], r_pts[2])
        avg_angle = (angle_l + angle_r) / 2

        self._update_state(avg_angle, True)

        # Stabilizacja wyświetlania (cooldown)
        current_time = time.time()
        if self.feedback != self._last_displayed_message:
            if current_time - self._last_feedback_time >= self._feedback_cooldown:
                self._last_displayed_message = self.feedback
                self._last_feedback_time = current_time

        return self.counter, self.stage, avg_angle, self._last_displayed_message