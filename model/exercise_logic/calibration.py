from model.exercise_logic.math_engine import get_distance


class CalibrationManager:
    def __init__(self, reference_length=0.5):
        self.user_height_scale = 1.0
        self.is_calibrated = False
        self.reference_length = reference_length

    def calibrate(self, shoulder, hip):
        """Oblicza skalę użytkownika na podstawie długości tułowia."""
        torso_length = get_distance(shoulder, hip)
        self.user_height_scale = torso_length / self.reference_length
        self.is_calibrated = True
        return self.user_height_scale

    def adjust(self, value):
        """Skaluje podaną wartość (np. margines błędu) do wzrostu."""
        return value * self.user_height_scale