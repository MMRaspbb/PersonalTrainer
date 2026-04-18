import random


class FeedbackManager:
    """Zarządza wszystkimi komunikatami tekstowymi i głosowymi w aplikacji."""

    def __init__(self):
        self.messages = {
            "squat": {
                "start": ["Zacznij przysiad", "Gotowy? Zrób przysiad!", "Pokaż co potrafisz!"],
                "good_rep": ["Świetny przysiad!", "Idealna głębokość!", "Doskonale, tak trzymaj!",
                             "Kolejny punkt dla Ciebie!"],
                "go_lower": ["Schodź niżej...", "Jeszcze trochę w dół.", "Pogłębij ten ruch!"],
                "go_up": ["Dobra głębokość, teraz w górę!", "W górę!", "Świetnie, wracaj!"],
                "extend_fully": ["Wracaj do pełnego wyprostu.", "Wyprostuj kolana do końca.", "Nie oszukuj na górze!"]
            },
            "pushup": {
                "start": ["Przyjmij pozycję do pompki", "Czekam na pierwszą pompkę."],
                "good_rep": ["Świetna pompka!", "Maszyna!", "Idealnie w punkt!"],
                "bad_back": ["Trzymaj plecy prosto!", "Popraw biodra!", "Nie wyginaj się w łuk!"],
                "rep_bad_form": ["Zaliczono, ale popraw BIODRA!", "Pompka zrobiona, ale trzymaj linię!",
                                 "Skup się na brzuchu!"],
                "go_up": ["Dobry zakres, wyciśnij to!"]
            }
        }

    def get(self, exercise: str, event: str) -> str:
        """
        Pobiera losowy komunikat dla danego ćwiczenia i zdarzenia.
        Przykład: get("squat", "good_rep") -> "Idealna głębokość!"
        """
        try:
            return random.choice(self.messages[exercise][event])
        except KeyError:
            return "..."