from dataclasses import dataclass

@dataclass
class ExerciseResponse:
    """Struktura danych zwracana przez handler."""
    counter: int
    stage: str
    message: str
    angle: float