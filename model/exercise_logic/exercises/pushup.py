from ..abstract.base_exercise import BaseExercise
from ..math_engine import calculate_angle, get_distance
from ..feedback_handler import FeedbackManager
from typing import Tuple, Dict, Any


class PushupCounter(BaseExercise):
    """
    Licznik pompek analizujący zagięcie ramion i osiowość ciała.

    Klasa monitoruje pracę ramion, sprawdza prostowę pleców
    i generuje informacje zwrotne w czasie rzeczywistym.
    """

    def __init__(self):
        """Inicjalizuje licznik pompek z progami dla różnych faz ruchu."""
        super().__init__(threshold_down=90.0, threshold_up=160.0)
        self.fm = FeedbackManager()
        self.feedback = self.fm.get("pushup", "start")
        self.arm_angle = 0.0
        self.body_angle = 0.0
        self._body_hidden_warned = False

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

        # Jeśli ciało nie jest widoczne, zwróć FALSE dla osiowości ale TRUE dla widoczności
        # Umożliwia to liczenie pompek bez kontroli pleców
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

        # Odległość między dłońmi
        hand_distance = get_distance(
            (l_wrist['x'], l_wrist['y']),
            (r_wrist['x'], r_wrist['y'])
        )

        # Szerokość barków
        shoulder_width = get_distance(
            (l_shoulder['x'], l_shoulder['y']),
            (r_shoulder['x'], r_shoulder['y'])
        )

        # Idealna wartość: 1.2 - 1.5
        ratio = hand_distance / shoulder_width if shoulder_width > 0 else 0

        if ratio < 1.0:
            return False, self.fm.get("pushup", "arms_too_narrow")
        elif ratio > 1.8:
            return False, self.fm.get("pushup", "arms_too_wide")

        return True, ""

    def _calculate_arm_angles(self, l_arm: list, r_arm: list) -> float:
        """
        Oblicza średni kąt zgięcia ramion (bark-łokieć).

        Używa tylko bark i łokieć, ignorując nadgarstek.
        Wartości około 180° to proste ramiona, <90° to ugiete.

        Args:
            l_arm: Lista współrzędnych lewego ramienia [shoulder, elbow, wrist]
            r_arm: Lista współrzędnych prawego ramienia [shoulder, elbow, wrist]

        Returns:
            Średni kąt zgięcia ramion (bark-łokieć)
        """
        # Używamy tylko bark i łokieć - pomijamy nadgarstek
        l_shoulder = l_arm[0]
        l_elbow = l_arm[1]
        r_shoulder = r_arm[0]
        r_elbow = r_arm[1]

        # Kąt bark-łokieć obliczamy względem pionu (0,1)
        l_virtual_down = (l_shoulder['x'], l_shoulder['y'] + 100)
        r_virtual_down = (r_shoulder['x'], r_shoulder['y'] + 100)

        ang_l = calculate_angle(
            (l_shoulder['x'], l_shoulder['y']),
            (l_elbow['x'], l_elbow['y']),
            l_virtual_down
        )
        ang_r = calculate_angle(
            (r_shoulder['x'], r_shoulder['y']),
            (r_elbow['x'], r_elbow['y']),
            r_virtual_down
        )
        return (ang_l + ang_r) / 2

    def _update_state(self, avg_arm_angle: float, is_straight: bool, is_body_visible: bool) -> None:
        """
        Aktualizuje stan maszyny stanowej i feedback na podstawie kąta ramion.

        Pompka jest zaliczana na podstawie ruchu ramion niezależnie od widoczności ciała.
        Jeśli ciało jest widoczne, informuje czy plecy są proste.

        Args:
            avg_arm_angle: Średni kąt zgięcia ramion
            is_straight: Czy plecy są proste (gdy ciało widoczne)
            is_body_visible: Czy ciało jest widoczne
        """
        if avg_arm_angle > 160:
            if self.stage == "down":
                # Zawsze zaliczamy, ale z różnym feedbackiem
                self.counter += 1
                if is_body_visible:
                    if is_straight:
                        self.feedback = self.fm.get("pushup", "good_rep")
                    else:
                        self.feedback = self.fm.get("pushup", "rep_bad_form")
                else:
                    # Ciało nie widoczne, ale ruchy OK
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

    def update(self, points: Dict[str, Any]) -> Tuple[int, str, float, str]:
        """
        Aktualizuje stan licznika na podstawie nowych współrzędnych punktów.

        Pompki są liczone na podstawie ruchu ramion.
        Widoczność ciała wpływa tylko na feedback o postawie, nie na liczenie.

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

        return self.counter, self.stage, self.arm_angle, self.feedback
