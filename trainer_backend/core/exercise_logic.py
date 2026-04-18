from .feedback import FeedbackManager
from .math_engine import calculate_angle, get_distance


class SquatCounter:
    """Licznik przysiadów z dynamicznym feedbackiem."""

    def __init__(self):
        self.counter = 0
        self.stage = "up"
        self.threshold_down = 90.0
        self.threshold_up = 160.0

        self.fm = FeedbackManager()
        self.feedback = self.fm.get("squat", "start")

    def update(self, hip, knee, ankle):
        angle = calculate_angle(hip, knee, ankle)

        if angle > self.threshold_up:
            if self.stage == "down":
                self.counter += 1
                self.feedback = self.fm.get("squat", "good_rep")
            self.stage = "up"

        elif angle < self.threshold_down:
            if self.stage == "up":
                self.feedback = self.fm.get("squat", "go_up")
            self.stage = "down"

        else:
            if self.stage == "up":
                self.feedback = self.fm.get("squat", "go_lower")
            elif self.stage == "down":
                self.feedback = self.fm.get("squat", "extend_fully")

        return self.counter, self.stage, angle, self.feedback


class PushupCounter:
    """Korektor pompek ze sprawdzaniem osiowości pleców i dynamicznym feedbackiem."""

    def __init__(self):
        self.counter = 0
        self.stage = "up"

        self.fm = FeedbackManager()
        self.feedback = self.fm.get("pushup", "start")

    def check_alignment(self, shoulder, hip, ankle):
        """Sprawdza czy plecy są w linii prostej (akceptowalny kąt 160-200 stopni)."""
        body_angle = calculate_angle(shoulder, hip, ankle)
        return 160 <= body_angle <= 200, body_angle

    def update(self, shoulder, elbow, wrist, hip, ankle):
        is_straight, body_angle = self.check_alignment(shoulder, hip, ankle)

        arm_angle = calculate_angle(shoulder, elbow, wrist)

        if arm_angle > 160:
            if self.stage == "down":
                if is_straight:
                    self.counter += 1
                    self.feedback = self.fm.get("pushup", "good_rep")
                else:
                    self.feedback = self.fm.get("pushup", "rep_bad_form")
            self.stage = "up"

        elif arm_angle < 90:
            self.stage = "down"
            if not is_straight:
                self.feedback = self.fm.get("pushup", "bad_back")
            else:
                self.feedback = self.fm.get("pushup", "go_up")

        return self.counter, self.stage, arm_angle, self.feedback


class CalibrationManager:
    def __init__(self):
        self.user_height_scale = 1.0
        self.is_calibrated = False

    def calibrate(self, shoulder, hip):
        """
        Oblicza skalę użytkownika na podstawie długości tułowia.
        Dystans między barkiem a biodrem to stabilna miara wzrostu.
        """
        torso_length = get_distance(shoulder, hip)

        # Skalujemy czułość algorytmów pod ten wynik.
        self.user_height_scale = torso_length / 0.5
        self.is_calibrated = True
        return self.user_height_scale

    def get_adjusted_threshold(self, base_threshold):
        """Dostosowuje próg ruchu (np. margines błędu) do wzrostu."""
        return base_threshold * self.user_height_scale