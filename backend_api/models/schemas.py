from pydantic import BaseModel,Field
from typing import List, Dict, Optional
from datetime import datetime

class Landmark(BaseModel):
    """
    Opisuje pojedynczy punkt na ciele wygenerowany przez MediaPipe.
    """
    x: float = Field(..., description="Znormalizowana współrzędna X (od 0.0 do 1.0)")
    y: float = Field(..., description="Znormalizowana współrzędna Y (od 0.0 do 1.0)")
    z: float = Field(..., description="Fizyczna głębia punktu względem środka bioder")
    visibility: float = Field(..., description="Prawdopodobieństwo, że punkt nie jest zasłonięty (0.0 - 1.0)")


class PoseDataIn(BaseModel):
    """
    Paczka danych, którą wysyła model AI (Osoba 1) do Twojego API po przetworzeniu jednej klatki.
    """
    landmarks: List[Landmark] = Field(..., min_length=33, max_length=33,
                                      description="Tablica dokładnie 33 punktów kluczowych 3D")

    timestamp: float = Field(..., description="Unikalny znacznik czasu ułamka sekundy z wideo")

class RealTimeFeedback(BaseModel):
    is_tracking: bool
    rep_count: int
    angle: float
    feedback :str  # Link do ExerciseDB po wykryciu błędu

# --- 4. WYJŚCIE RAPORT: Co wysyłasz do Javy (REST API) ---
class JavaWorkoutSummary(BaseModel):
    user_id: str
    exercise_type: str  # Np. "squat"
    reps_completed: int
    accuracy_score: float  # % poprawności technicznej
    alerts_count: int  # Ile razy wystąpił błąd postawy
    session_duration: int  # Sekundy
    timestamp_end: datetime = Field(default_factory=datetime.now)