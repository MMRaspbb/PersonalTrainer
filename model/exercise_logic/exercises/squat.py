from ..abstract.base_exercise import BaseExercise
from ..math_engine import calculate_angle

class SquatCounter(BaseExercise):
    def __init__(self):
        super().__init__(threshold_down=90.0, threshold_up=160.0)

    def update(self, hip, knee, ankle):
        angle = calculate_angle(hip, knee, ankle)
        if self._process_state(angle):
            self.counter += 1
        return self.counter, self.stage, angle