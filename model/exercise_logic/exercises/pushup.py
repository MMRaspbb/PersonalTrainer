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
        """Inicjalizuje licznik pompek z parametrami z ParametersManager"""
        super().__init__(exercise_type=ExerciseType.PUSHUP)

        self.fm = FeedbackManager()
        self.feedback = self.fm.get("pushup", "start")
        self.arm_angle = 0.0
        self.body_angle = 0.0
        self._body_hidden_warned = False

        # Pobierz parametry z ParametersManager
        params = ParametersManager.get_parameters(ExerciseType.PUSHUP)
        self._feedback_cooldown = params.feedback.cooldown_seconds
        self._last_feedback_time = 0.0
        self._last_feedback_message = ""

        # Custom parametry dla pompek
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
        """
        Waliduje widoczność wymaganych punktów anatomicznych.

        Args:
            points: Słownik ze współrzędnymi punktów
            required_keys: Lista wymaganych kluczy

        Returns:
            Krotka (czy_widoczne, komunikat_błędu)
        """
        for key in required_keys:
            if key not in points or points[key] is None:
                if "arm" in str(required_keys):
                    return False, self.fm.get("pushup", "both_arms_visible")
                return False, self.fm.get("pushup", "body_hidden")
        return True, ""

    def _check_alignment(self, points: Dict[str, Any]) -> Tuple[bool, float, bool]:
        """
        Sprawdza osiowość (prostowę pleców) dla obu stron ciała.

        Idealna linia powinna być prawie prosta (160-200 stopni)
        Zwraca też informację czy ciało jest w ogóle widoczne.

        Args:
            points: Słownik ze współrzędnymi punktów

        Returns:
            Krotka (czy_proste_plecy, kąt_ciała, czy_widoczne)
        """
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

        # Prawidłowe wyprostu to 160-200 stopni
        return (160 <= avg_body <= 200), avg_body, True

    def _check_arm_width(self, points: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Sprawdza szerokość rozstawienia rąk podczas pompki.

        Idealna szerokość to około 1.2x - 1.5x szerokości barków.

        Args:
            points: Słownik ze współrzędnymi punktów

        Returns:
            Krotka (czy_szerokość_OK, komunikat_feedback)
        """
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

        if ratio < 1.0:
            return False, self.fm.get("pushup", "arms_too_narrow")
        elif ratio > 1.8:
            return False, self.fm.get("pushup", "arms_too_wide")

        return True, ""

    def _calculate_arm_angles(self, l_arm: list, r_arm: list) -> float:
        """
        Oblicza średni kąt zgięcia w łokciach z interpolacją.

        Logika:
        - visibility >= 0.4: używa rzeczywistych współrzędnych
        - visibility < 0.4: interpoluje z historii (numpy.interp)
        - fallback: wirtualny punkt
        """
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

        ang_l = get_reliable_angle(l_arm, 'l_arm')
        ang_r = get_reliable_angle(r_arm, 'r_arm')

        return (ang_l + ang_r) / 2

    def _update_state(self, avg_arm_angle: float, is_straight: bool, is_body_visible: bool) -> None:
        """
        Aktualizuje stan maszyny stanowej i feedback na podstawie kąta ramion.

        Args:
            avg_arm_angle: Średni kąt zgięcia ramion
            is_straight: Czy plecy są proste (gdy ciało widoczne)
            is_body_visible: Czy ciało jest widoczne
        """
        if avg_arm_angle > 160:
            if self.stage == "down":
                self.counter += 1
                if is_body_visible:
                    if is_straight:
                        self.feedback = self.fm.get("pushup", "good_rep")
                    else:
                        self.feedback = self.fm.get("pushup", "rep_bad_form")
                else:
                    self.feedback = self.fm.get("pushup", "good_rep")
            self.stage = "up"

        elif avg_arm_angle < 90:
            self.stage = "down"
            if is_body_visible:
                if is_straight:
                    self.feedback = self.fm.get("pushup", "go_up")
                else:
                    self.feedback = self.fm.get("pushup", "bad_back")
            else:
                self.feedback = self.fm.get("pushup", "go_up")

    def _apply_feedback_cooldown(self, current_time: float) -> str:
        """
        Zastosuj cooldown dla feedback'u.

        Args:
            current_time: Aktualny czas (time.time())

        Returns:
            Feedback do wyświetlenia (nigdy nie pusty string)
        """
        if (self.feedback != self._last_feedback_message or
            current_time - self._last_feedback_time >= self._feedback_cooldown):

            self._last_feedback_message = self.feedback
            self._last_feedback_time = current_time

        return self._last_feedback_message

    def update(self, points: Dict[str, Any]) -> Tuple[int, str, float, str]:
        """
        Aktualizuje stan licznika na podstawie nowych współrzędnych punktów.

        Args:
            points: Słownik ze współrzędnymi punktów anatomicznych w formacie:
                   {'l_shoulder': {'x': float, 'y': float}, ...}

        Returns:
            Krotka (licznik, stan, kąt_ramion, komunikat_feedback)
        """
        arm_keys = ['l_shoulder', 'l_elbow', 'l_wrist', 'r_shoulder', 'r_elbow', 'r_wrist']
        is_arms_visible, arm_error = self._validate_visible_points(points, arm_keys)

        if not is_arms_visible:
            return self.counter, self.stage, 0.0, arm_error

        is_width_ok, width_feedback = self._check_arm_width(points)
        if not is_width_ok:
            self.feedback = width_feedback
            return self.counter, self.stage, 0.0, width_feedback

        l_arm = [points['l_shoulder'], points['l_elbow'], points['l_wrist']]
        r_arm = [points['r_shoulder'], points['r_elbow'], points['r_wrist']]

        is_straight, body_angle, is_body_visible = self._check_alignment(points)

        self.arm_angle = self._calculate_arm_angles(l_arm, r_arm)

        self._update_state(self.arm_angle, is_straight, is_body_visible)

        if not is_body_visible and self.feedback not in [self.fm.get("pushup", "body_hidden"),
                                                          self.fm.get("pushup", "both_arms_visible"),
                                                          self.fm.get("pushup", "arms_too_wide"),
                                                          self.fm.get("pushup", "arms_too_narrow")]:
            if not self._body_hidden_warned:
                self.feedback = self.fm.get("pushup", "body_hidden")
                self._body_hidden_warned = True

        current_time = time.time()
        feedback_to_return = self._apply_feedback_cooldown(current_time)

        return self.counter, self.stage, self.arm_angle, feedback_to_return
