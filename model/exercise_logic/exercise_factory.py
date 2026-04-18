from .exercises.squat import SquatCounter
from .exercises.pushup import PushupCounter

class ExerciseFactory:
    _EXERCISES = {
        "squat": SquatCounter,
        "pushup": PushupCounter
    }

    @classmethod
    def get_exercise(cls, name):
        exercise_class = cls._EXERCISES.get(name.lower())
        if not exercise_class:
            raise ValueError(f"Nieznane cwiczenie: {name}")
        return exercise_class()