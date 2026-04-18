from model.exercise_logic.abstract.base_exercise import BaseExercise
from model.exercise_logic.math_engine import calculate_angle


class PushupCounter(BaseExercise):
    """Korektor pompek z analizą postawy."""

    def __init__(self):
        super().__init__(threshold_down=90.0, threshold_up=160.0)
        self.feedback = ""

    def _is_back_straight(self, shoulder, hip, ankle):
        """Wewnętrzna walidacja osiowości kręgosłupa."""
        body_angle = calculate_angle(shoulder, hip, ankle)
        return 160 <= body_angle <= 200, body_angle

    def update(self, shoulder, elbow, wrist, hip, ankle):
        arm_angle = calculate_angle(shoulder, elbow, wrist)
        is_straight, body_angle = self._is_back_straight(shoulder, hip, ankle)

        if self._process_state(arm_angle):
            if is_straight:
                self.counter += 1
                self.feedback = "Świetna technika!"
            else:
                # W oryginalnym kodzie licznik nie rósł przy złej technice
                self.feedback = "Pompka wykonana, ale popraw BIODRA!"

        return self.counter, self.stage, self.feedback, arm_angle