from pydantic import BaseModel,Field
from typing import List, Dict, Optional

class Landmark(BaseModel):
    """
    Opisuje pojedynczy punkt na ciele wygenerowany przez MediaPipe.
    """
    x: float = Field(..., description="Znormalizowana współrzędna X (od 0.0 do 1.0)")
    y: float = Field(..., description="Znormalizowana współrzędna Y (od 0.0 do 1.0)")
    z: float = Field(..., description="Fizyczna głębia punktu względem środka bioder")
    visibility: float = Field(..., description="Prawdopodobieństwo, że punkt nie jest zasłonięty (0.0 - 1.0)")

