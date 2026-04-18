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

    Parametry są pobierane automatycznie z ParametersManager.
    """

    def __init__(self):
        """Inicjalizuje licznik pompek z parametrami z ParametersManager."""
        super().__init__(exercise_type=ExerciseType.PUSHUP)

        self.fm = FeedbackManager()
        self.feedback = self.fm.get("pushup", "start")
        self.arm_angle = 0.0
        self.body_angle = 0.0
        self._body_hidden_warned = False

        params = ParametersManager.get_parameters(ExerciseType.PUSHUP)
        self._feedback_cooldown = params.feedback.cooldown_seconds
        self._last_feedback_time = 0.0
        self._last_feedback_message = ""

        # Specyficzne parametry dla pompek
        self._arm_width_min = ParametersManager.get_custom_param(
            ExerciseType.PUSHUP, "arm_width_min", 1.0
        )
        self._arm_width_max = ParametersManager.get_custom_param(
            ExerciseType.PUSHUP, "arm_width_max", 1.8
        )
        self._body_alignment_tolerance = ParametersManager.get_custom_param(
            ExerciseType.PUSHUP, "body_alignment_tolerance", 20.0
        )
        self._min_arm_symmetry = ParametersManager.get_custom_param(
            ExerciseType.PUSHUP, "min_arm_symmetry", 0.8
        )

    def _validate_visible_points(self, points: Dict[str, Any], required_keys: list) -> Tuple[bool, str]:
        """Waliduje widoczność wymaganych punktów anatomicznych."""
        for key in required_keys:
            if key not in points or points[key] is None:
                if "arm" in str(required_keys):
                    return False, self.fm.get("pushup", "both_arms_visible")
                return False, self.fm.get("pushup", "body_hidden")
        return True, ""

    def _check_alignment(self, points: Dict[str, Any]) -> Tuple[bool, float, bool]:
        """Sprawdza osiowość (prostowę pleców) dla obu stron ciała."""
        body_keys = ['l_shoulder', 'l_hip', 'l_ankle', 'r_shoulder', 'r_hip', 'r_ankle']
        is_visible, _ = self._validate_visible_points(points, body_keys)

        if not is_visible:
            return False, 0.0, False

        l_body = [points['l_shoulder'], points['l_hip'], points['l_ankle']]
        r_body = [points['r_shoulder'], points['r_hip'], points['r_ankle']]

        ang_l = calculate_angle(
            (l_body[0]['x'], l_body[0]['y']),
            (l_body[1]['x'], l_body[1]['y']),
            (l_body[2]['x'], l_body[2]['y'])
        )
        ang_r = calculate_angle(
            (r_body[0]['x'], r_body[0]['y']),
            (r_body[1]['x'], r_body[1]['y']),
            (r_body[2]['x'], r_body[2]['y'])
        )

        avg_body = (ang_l + ang_r) / 2
        self.body_angle = avg_body
        return (160 <= avg_body <= 200), avg_body, True

    def _check_arm_width(self, points: Dict[str, Any]) -> Tuple[bool, str]:
        """Sprawdza szerokość rozstawienia rąk podczas pompki."""
        l_wrist = points['l_wrist']
        r_wrist = points['r_wrist']
        l_shoulder = points['l_shoulder']
        r_shoulder = points['r_shoulder']

        hand_distance = get_distance(
            (l_wrist['x'], l_wrist['y']),
            (r_wrist['x'], r_wrist['y'])
        )

        shoulder_width = get_distance(
            (l_shoulder['x'], l_shoulder['y']),
            (r_shoulder['x'], r_shoulder['y'])
        )

        ratio = hand_distance / shoulder_width if shoulder_width > 0 else 0

        if ratio < self._arm_width_min:
            return False, self.fm.get("pushup", "arms_too_narrow")
        elif ratio > self._arm_width_max:
            return False, self.fm.get("pushup", "arms_too_wide")

        return True, ""

    def _calculate_arm_angles(self, l_arm: list, r_arm: list, l_visible: bool=True, r_visible: bool=True) -> float:
        """Oblicza średni kąt zgięcia w łokciach z uwzględnieniem tylko widocznych ramion."""
        def get_reliable_angle(arm, limb):
            s = arm[0]  # shoulder
            e = arm[1]  # elbow
            w = arm[2]  # wrist

            visibility = w.get('visibility', 1.0) if isinstance(w, dict) else 1.0

            # Użyj interpolacji - auto decyduje czy interpolować
            return calculate_angle_with_interpolation(
                a=s, b=e, c=w,
                c_visibility=visibility,
                limb=limb,
                use_interpolation=True
            )

        angles = []
        if l_visible and l_arm:
            angles.append(get_reliable_angle(l_arm, 'l_arm'))
        if r_visible and r_arm:
            angles.append(get_reliable_angle(r_arm, 'r_arm'))

        if not angles:
            return 0.0

        return sum(angles) / len(angles)

    def _update_state(self, avg_arm_angle: float) -> None:
        """
        Aktualizuje stan maszyny stanowej i feedback na podstawie kąta ramion.
        """
        if avg_arm_angle > 160:
            if self.stage == "down":
                self.counter += 1
                self.feedback = self.fm.get("pushup", "good_rep")
            self.stage = "up"

        elif avg_arm_angle < 90:
            if self.stage == "up":
                self.feedback = self.fm.get("pushup", "go_up")
            self.stage = "down"
        else:
            if self.stage == "up":
                self.feedback = self.fm.get("pushup", "go_lower")
            elif self.stage == "down":
                self.feedback = self.fm.get("pushup", "extend_fully")

    def _apply_feedback_cooldown(self, current_time: float) -> str:
        """Blokuje migotanie UI. Priorytetowe wiadomości ('good_rep') przerywają cooldown."""
        time_passed = current_time - self._last_feedback_time
        priority_messages = [self.fm.get("pushup", "good_rep")]

        if time_passed >= self._feedback_cooldown or self.feedback in priority_messages:
            if self.feedback != self._last_feedback_message:
                self._last_feedback_message = self.feedback
                self._last_feedback_time = current_time

        return self._last_feedback_message

    def update(self, points: Dict[str, Any]) -> Tuple[int, str, float, str]:
        """Aktualizuje stan licznika na podstawie nowych współrzędnych punktów."""
        l_keys = ['l_shoulder', 'l_elbow', 'l_wrist']
        r_keys = ['r_shoulder', 'r_elbow', 'r_wrist']

        l_visible = all(k in points and points[k] is not None for k in l_keys)
        r_visible = all(k in points and points[k] is not None for k in r_keys)

        if not l_visible and not r_visible:
            return self.counter, self.stage, 0.0, self.fm.get("pushup", "both_arms_visible")

        l_arm = [points[k] for k in l_keys] if l_visible else []
        r_arm = [points[k] for k in r_keys] if r_visible else []

        self.arm_angle = self._calculate_arm_angles(l_arm, r_arm, l_visible, r_visible)

        self._update_state(self.arm_angle)

        current_time = time.time()
        feedback_to_return = self._apply_feedback_cooldown(current_time)

        return self.counter, self.stage, self.arm_angle, feedback_to_return
