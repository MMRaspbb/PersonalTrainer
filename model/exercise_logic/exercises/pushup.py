from ..abstract.base_exercise import BaseExercise
from ..math_engine import calculate_angle, get_distance, calculate_angle_with_interpolation
from ..feedback_handler import FeedbackManager
from ..parameters import ParametersManager, ExerciseType
from typing import Tuple, Dict, Any
import time


class PushupCounter(BaseExercise):
    """
    Licznik pompek analizujący zagięcie ramion i osiowość ciała.

    Klasa monitoruje pracę ramion, sprawdza prostowę pleców
    i generuje informacje zwrotne w czasie rzeczywistym.
    Wykorzystuje system zdarzeń (event-based feedback) dla stabilności UI.
    """

    def __init__(self):
        """Inicjalizuje licznik pompek z parametrami z ParametersManager."""
        super().__init__(exercise_type=ExerciseType.PUSHUP)

        self.fm = FeedbackManager()
        self.feedback = self.fm.get("pushup", "start")

        # System stabilizacji feedbacku (anti-flicker)
        self._current_event = "start"
        self._last_feedback_time = 0.0
        self._last_feedback_message = self.feedback

        # Pobranie parametrów z ParametersManager
        params = ParametersManager.get_parameters(ExerciseType.PUSHUP)
        self._feedback_cooldown = params.feedback.cooldown_seconds

        # Specyficzne parametry dla pompek
        self._arm_width_min = ParametersManager.get_custom_param(
            ExerciseType.PUSHUP, "arm_width_min", 1.0
        )
        self._arm_width_max = ParametersManager.get_custom_param(
            ExerciseType.PUSHUP, "arm_width_max", 1.8
        )

        self.arm_angle = 0.0
        self.body_angle = 0.0

    def _update_state(self, avg_arm_angle: float, is_straight: bool, is_body_visible: bool) -> None:
        """
        Aktualizuje stan maszyny stanowej i wybiera zdarzenie feedbacku.
        Nowa treść jest losowana tylko przy faktycznej zmianie zdarzenia.
        """
        new_event = self._current_event

        if avg_arm_angle > 160:
            if self.stage == "down":
                self.counter += 1
                if is_body_visible:
                    new_event = "good_rep" if is_straight else "rep_bad_form"
                else:
                    new_event = "good_rep"
            self.stage = "up"
        elif avg_arm_angle < 100:  # Próg z ParametersManager (100.0)
            self.stage = "down"
            if is_body_visible:
                new_event = "go_up" if is_straight else "bad_back"
            else:
                new_event = "go_up"

        # Aktualizuj feedback tylko przy zmianie kategorii zdarzenia
        if new_event != self._current_event:
            self._current_event = new_event
            self.feedback = self.fm.get("pushup", new_event)

    def _apply_feedback_cooldown(self, current_time: float) -> str:
        """
        Zapewnia stabilność wyświetlanego tekstu.
        Zwraca ostatnią wiadomość, dopóki nie upłynie cooldown dla nowej.
        """
        if (self.feedback != self._last_feedback_message and
                current_time - self._last_feedback_time >= self._feedback_cooldown):
            self._last_feedback_message = self.feedback
            self._last_feedback_time = current_time

        return self._last_feedback_message

    def _check_alignment(self, points: Dict[str, Any]) -> Tuple[bool, float, bool]:
        """Weryfikuje osiowość tułowia (prostowę pleców)."""
        body_keys = ['l_shoulder', 'l_hip', 'l_ankle', 'r_shoulder', 'r_hip', 'r_ankle']
        if not all(key in points and points[key] is not None for key in body_keys):
            return False, 0.0, False

        # Obliczanie kąta dla obu stron ciała
        ang_l = calculate_angle(points['l_shoulder'], points['l_hip'], points['l_ankle'])
        ang_r = calculate_angle(points['r_shoulder'], points['r_hip'], points['r_ankle'])

        avg_body = (ang_l + ang_r) / 2
        return (160 <= avg_body <= 200), avg_body, True

    def _check_arm_width(self, points: Dict[str, Any]) -> Tuple[bool, str]:
        """Sprawdza szerokość rozstawienia dłoni względem barków."""
        l_sh, r_sh = points['l_shoulder'], points['r_shoulder']
        l_wr, r_wr = points['l_wrist'], points['r_wrist']

        shoulder_width = get_distance(l_sh, r_sh)
        hand_width = get_distance(l_wr, r_wr)

        ratio = hand_width / shoulder_width if shoulder_width > 0 else 0

        if ratio < self._arm_width_min:
            return False, self.fm.get("pushup", "arms_too_narrow")
        elif ratio > self._arm_width_max:
            return False, self.fm.get("pushup", "arms_too_wide")

        return True, ""

    def _calculate_arm_angles(self, points: Dict[str, Any]) -> float:
        """Oblicza średni kąt zgięcia ramion z interpolacją."""

        def get_limb_angle(s_key, e_key, w_key, side):
            s, e, w = points[s_key], points[e_key], points[w_key]
            visibility = w.get('visibility', 1.0) if isinstance(w, dict) else 1.0
            return calculate_angle_with_interpolation(s, e, w, visibility, side, True)

        ang_l = get_limb_angle('l_shoulder', 'l_elbow', 'l_wrist', 'l_arm')
        ang_r = get_limb_angle('r_shoulder', 'r_elbow', 'r_wrist', 'r_arm')
        return (ang_l + ang_r) / 2

    def update(self, points: Dict[str, Any]) -> Tuple[int, str, float, str]:
        """Główna metoda aktualizacji na podstawie punktów anatomicznych."""
        # 1. Walidacja widoczności rąk
        arm_keys = ['l_shoulder', 'l_elbow', 'l_wrist', 'r_shoulder', 'r_elbow', 'r_wrist']
        for key in arm_keys:
            if key not in points or points[key] is None:
                return self.counter, self.stage, 0.0, self.fm.get("pushup", "both_arms_visible")

        # 2. Sprawdzenie parametrów technicznych
        is_width_ok, width_feedback = self._check_arm_width(points)
        if not is_width_ok:
            self.feedback = width_feedback
            return self.counter, self.stage, 0.0, self._apply_feedback_cooldown(time.time())

        # 3. Analiza osiowości i kątów
        is_straight, self.body_angle, is_body_visible = self._check_alignment(points)
        self.arm_angle = self._calculate_arm_angles(points)

        # 4. Procesowanie stanu
        self._update_state(self.arm_angle, is_straight, is_body_visible)

        # 5. Ostrzeżenie o braku widoczności dolnej partii ciała
        if not is_body_visible and self._current_event not in ["body_hidden", "both_arms_visible"]:
            self.feedback = self.fm.get("pushup", "body_hidden")

        return self.counter, self.stage, self.arm_angle, self._apply_feedback_cooldown(time.time())