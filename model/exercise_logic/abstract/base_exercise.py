from abc import ABC, abstractmethod
from ..math_engine import calculate_angle, get_distance

class BaseExercise(ABC):
    def __init__(self, threshold_down, threshold_up):
        self.counter = 0
        self.stage = "up"
        self.threshold_down = threshold_down
        self.threshold_up = threshold_up

    def _process_state(self, current_angle):
        rep_completed = False
        if current_angle < self.threshold_down:
            self.stage = "down"
        if current_angle > self.threshold_up and self.stage == "down":
            self.stage = "up"
            rep_completed = True
        return rep_completed

    @abstractmethod
    def update(self, *args, **kwargs):
        pass