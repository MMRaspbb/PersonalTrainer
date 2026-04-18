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

    def _check_alignment(self, points: Dict[str, Any]) -> Tuple[bool, float]:
        """
        Sprawdza osiowość (prostowę pleców) dla obu stron ciała.

        Idealna linia powinna być prawie prosta (160-200 stopni)

        Args:
            points: Słownik ze współrzędnymi punktów

        Returns:
            Krotka (czy_proste_plecy, kąt_ciała)
        """
        body_keys = ['l_shoulder', 'l_hip', 'l_ankle', 'r_shoulder', 'r_hip', 'r_ankle']
        is_visible, _ = self._validate_visible_points(points, body_keys)

        if not is_visible:
            return False, 0.0

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
        return (160 <= avg_body <= 200), avg_body

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

        # Stosunek szerokości dłoni do szerokości barków
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
        # Obliczamy wektor z barku do łokcia i patrzymy na jego kąt
        l_shoulder = l_arm[0]
        l_elbow = l_arm[1]
        r_shoulder = r_arm[0]
        r_elbow = r_arm[1]

        # Kąt bark-łokieć obliczamy względem pionu (0,1)
        # Używamy calculate_angle z fikcyjnym trzecim punktem poniżej barku
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

    def _update_state(self, avg_arm_angle: float, is_straight: bool) -> None:
        """
        Aktualizuje stan maszyny stanowej i feedback na podstawie kąta ramion.

        Args:
            avg_arm_angle: Średni kąt zgięcia ramion
            is_straight: Czy plecy są proste
        """
        if avg_arm_angle > 160:
            # Ramiona wyprostowane (górna pozycja)
            if self.stage == "down":
                if is_straight:
                    self.counter += 1
                    self.feedback = self.fm.get("pushup", "good_rep")
                else:
                    self.feedback = self.fm.get("pushup", "rep_bad_form")
            self.stage = "up"

        elif avg_arm_angle < 90:
            # Ramiona ugięte (dolna pozycja)
            self.stage = "down"
            if is_straight:
                self.feedback = self.fm.get("pushup", "go_up")
            else:
                self.feedback = self.fm.get("pushup", "bad_back")

    def update(self, points: Dict[str, Any]) -> Tuple[int, str, float, str]:
        """
        Aktualizuje stan licznika na podstawie nowych współrzędnych punktów.

        Args:
            points: Słownik ze współrzędnymi punktów anatomicznych w formacie:
                   {'l_shoulder': {'x': float, 'y': float}, ...}

        Returns:
            Krotka (licznik, stan, kąt_ramion, komunikat_feedback)
        """
        # Walidacja widoczności ramion
        arm_keys = ['l_shoulder', 'l_elbow', 'l_wrist', 'r_shoulder', 'r_elbow', 'r_wrist']
        is_arms_visible, arm_error = self._validate_visible_points(points, arm_keys)

        if not is_arms_visible:
            return self.counter, self.stage, 0.0, arm_error

        # Sprawdzenie szerokości pompek
        is_width_ok, width_feedback = self._check_arm_width(points)
        if not is_width_ok:
            self.feedback = width_feedback
            return self.counter, self.stage, 0.0, width_feedback

        # Przygotowanie danych
        l_arm = [points['l_shoulder'], points['l_elbow'], points['l_wrist']]
        r_arm = [points['r_shoulder'], points['r_elbow'], points['r_wrist']]

        # Sprawdzenie osiowości ciała
        is_straight, body_angle = self._check_alignment(points)

        # Jeśli ciało jest zasłonięte, zwróć komunikat
        if not is_straight and body_angle == 0.0:
            return self.counter, self.stage, 0.0, self.fm.get("pushup", "body_hidden")

        # Obliczenie kąta ramion
        self.arm_angle = self._calculate_arm_angles(l_arm, r_arm)

        # Aktualizacja stanu
        self._update_state(self.arm_angle, is_straight)

        return self.counter, self.stage, self.arm_angle, self.feedback
