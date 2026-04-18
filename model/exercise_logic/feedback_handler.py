import random

class FeedbackManager:
    """Zarządza wszystkimi komunikatami tekstowymi w aplikacji."""

    def __init__(self):
        self.messages = {
            "squat": {
                "start": ["Zacznij przysiad", "Pokaż co potrafisz!"],
                "good_rep": ["Świetny przysiad!", "Idealna głębokość!", "Doskonale!"],
                "go_lower": ["Schodź niżej...", "Jeszcze trochę w dół."],
                "go_up": ["Dobra głębokość, teraz w górę!", "W górę!"],
                "extend_fully": ["Wracaj do pełnego wyprostu.", "Nie oszukuj na górze!"]
            },
            "pushup": {
                "start": ["Przyjmij pozycję do pompki", "Czekam na pierwszą pompkę."],
                "good_rep": ["Świetna pompka!", "Maszyna!"],
                "bad_back": ["Trzymaj plecy prosto!", "Popraw biodra!"],
                "rep_bad_form": ["Zaliczono, ale popraw BIODRA!", "Skup się na brzuchu!"],
                "go_up": ["Dobry zakres, wyciśnij to!"]
            }
        }

    def get(self, exercise: str, event: str) -> str:
        """Pobiera losowy komunikat dla danego zdarzenia."""
        try:
            return random.choice(self.messages[exercise][event])
        except (KeyError, IndexError):
            return "..."