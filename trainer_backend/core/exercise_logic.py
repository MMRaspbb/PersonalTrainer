from .math_engine import calculate_angle, get_distance



class SquatCounter:
    """Licznik przysiadów z kontrolą głębokości (90 stopni)."""

    def __init__(self):
        self.counter = 0
        self.stage = "up"
        self.threshold_down = 90.0
        self.threshold_up = 160.0

    def update(self, hip, knee, ankle):
        angle = calculate_angle(hip, knee, ankle)

        if angle < self.threshold_down:
            self.stage = "down"

        if angle > self.threshold_up and self.stage == "down":
            self.counter += 1
            self.stage = "up"

        return self.counter, self.stage, angle


class PushupCounter:
    """Korektor pompek ze sprawdzaniem osiowości kręgosłupa."""

    def __init__(self):
        self.counter = 0
        self.stage = "up"
        self.feedback = ""

    def check_alignment(self, shoulder, hip, ankle):
        """Sprawdza, czy plecy są w linii prostej."""
        body_angle = calculate_angle(shoulder, hip, ankle)
        return 160 <= body_angle <= 200, body_angle

    def update(self, shoulder, elbow, wrist, hip, ankle):
        is_straight, body_angle = self.check_alignment(shoulder, hip, ankle)
        arm_angle = calculate_angle(shoulder, elbow, wrist)

        if arm_angle > 160:
            if self.stage == "down":
                if is_straight:
                    self.counter += 1
                    self.feedback = "Świetna technika!"
                else:
                    self.feedback = "Pompka wykonana, ale popraw BIODRA!"
            self.stage = "up"
        elif arm_angle < 90:
            self.stage = "down"

        return self.counter, self.stage, self.feedback, arm_angle


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