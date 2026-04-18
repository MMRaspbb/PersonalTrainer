# model/exercise_logic/parameters.py - Centralna kontrola parametrów ćwiczeń

"""
Moduł zarządzający wszystkimi parametrami ćwiczeń.
Umożliwia łatwą konfigurację progów, cooldown'ów i innych ustawień
bez modyfikowania kodu logiki ćwiczeń.
"""

from dataclasses import dataclass
from typing import Dict, Any
from enum import Enum


class ExerciseType(Enum):
    """Dostępne typy ćwiczeń"""
    SQUAT = "squat"
    PUSHUP = "pushup"


@dataclass
class ExerciseThresholds:
    """Progi kątów dla ćwiczenia"""
    threshold_down: float
    threshold_up: float


@dataclass
class FeedbackSettings:
    """Ustawienia dla systemu feedback'u"""
    cooldown_seconds: float
    enable_cooldown: bool = True


@dataclass
class VisibilitySettings:
    """Ustawienia dla obsługi widoczności punktów"""
    visibility_threshold: float = 0.4
    use_fallback: bool = True
    fallback_tolerance: float = 0.1


@dataclass
class ExerciseParameters:
    """Kompletne parametry dla ćwiczenia"""
    exercise_type: ExerciseType
    thresholds: ExerciseThresholds
    feedback: FeedbackSettings
    visibility: VisibilitySettings
    custom_params: Dict[str, Any] = None

    def __post_init__(self):
        if self.custom_params is None:
            self.custom_params = {}


class ParameterValidator:
    """Walidator parametrów ćwiczeń"""

    @staticmethod
    def validate_thresholds(thresholds: ExerciseThresholds) -> bool:
        """Sprawdza czy progi są poprawne"""
        if not isinstance(thresholds.threshold_down, (int, float)):
            raise ValueError("threshold_down musi być liczbą")
        if not isinstance(thresholds.threshold_up, (int, float)):
            raise ValueError("threshold_up musi być liczbą")

        if thresholds.threshold_down >= thresholds.threshold_up:
            raise ValueError(
                f"threshold_down ({thresholds.threshold_down}) "
                f"musi być mniejszy niż threshold_up ({thresholds.threshold_up})"
            )

        if thresholds.threshold_down < 0 or thresholds.threshold_up > 180:
            raise ValueError("Progi kątów muszą być w zakresie 0-180 stopni")

        return True

    @staticmethod
    def validate_feedback_settings(feedback: FeedbackSettings) -> bool:
        """Sprawdza czy ustawienia feedback'u są poprawne"""
        if feedback.cooldown_seconds < 0:
            raise ValueError("cooldown_seconds nie może być ujemny")

        if feedback.cooldown_seconds > 60:
            raise ValueError("cooldown_seconds nie powinien przekraczać 60 sekund")

        return True

    @staticmethod
    def validate_visibility_settings(visibility: VisibilitySettings) -> bool:
        """Sprawdza czy ustawienia widoczności są poprawne"""
        if not 0.0 <= visibility.visibility_threshold <= 1.0:
            raise ValueError("visibility_threshold musi być w zakresie 0.0-1.0")

        if not 0.0 <= visibility.fallback_tolerance <= 1.0:
            raise ValueError("fallback_tolerance musi być w zakresie 0.0-1.0")

        return True

    @staticmethod
    def validate_parameters(params: ExerciseParameters) -> bool:
        """Waliduje wszystkie parametry"""
        ParameterValidator.validate_thresholds(params.thresholds)
        ParameterValidator.validate_feedback_settings(params.feedback)
        ParameterValidator.validate_visibility_settings(params.visibility)
        return True


class ParametersManager:
    """Menedżer parametrów - dostarcza domyślne i custom parametry"""

    # Domyślne parametry dla przysiadów
    SQUAT_DEFAULTS = ExerciseParameters(
        exercise_type=ExerciseType.SQUAT,
        thresholds=ExerciseThresholds(
            threshold_down=90.0,      # Pełne zgięcie
            threshold_up=160.0        # Pełny wyprost
        ),
        feedback=FeedbackSettings(
            cooldown_seconds=2.0,
            enable_cooldown=True
        ),
        visibility=VisibilitySettings(
            visibility_threshold=0.4,
            use_fallback=True
        ),
        custom_params={
            "min_angle_variance": 5.0,  # Min różnica między lewą a prawą nogą
            "stability_frames": 3,       # Ilość klatek do stabilizacji
        }
    )

    # Domyślne parametry dla pompek
    PUSHUP_DEFAULTS = ExerciseParameters(
        exercise_type=ExerciseType.PUSHUP,
        thresholds=ExerciseThresholds(
            threshold_down=100.0,      # Ugiete ramiona
            threshold_up=160.0        # Wyprostowane ramiona
        ),
        feedback=FeedbackSettings(
            cooldown_seconds=2.0,
            enable_cooldown=True
        ),
        visibility=VisibilitySettings(
            visibility_threshold=0.4,
            use_fallback=True,
            fallback_tolerance=0.15
        ),
        custom_params={
            "arm_width_min": 1.0,         # Min stosunek szerokości
            "arm_width_max": 1.8,         # Max stosunek szerokości
            "body_alignment_tolerance": 20.0,  # Tolerancja wyrównania ciała
            "min_arm_symmetry": 0.8,      # Min symetria ramion
        }
    )

    # Storage dla custom parametrów
    _custom_params: Dict[ExerciseType, ExerciseParameters] = {}

    @classmethod
    def get_parameters(cls, exercise_type: ExerciseType) -> ExerciseParameters:
        """
        Pobierz parametry dla danego ćwiczenia.
        Najpierw szuka custom parametrów, potem domyślne.
        """
        if exercise_type in cls._custom_params:
            return cls._custom_params[exercise_type]

        if exercise_type == ExerciseType.SQUAT:
            return cls.SQUAT_DEFAULTS
        elif exercise_type == ExerciseType.PUSHUP:
            return cls.PUSHUP_DEFAULTS
        else:
            raise ValueError(f"Nieznane ćwiczenie: {exercise_type}")

    @classmethod
    def set_parameters(cls, exercise_type: ExerciseType,
                      parameters: ExerciseParameters) -> None:
        """
        Ustaw custom parametry dla danego ćwiczenia.
        Waliduje parametry przed zapisaniem.
        """
        ParameterValidator.validate_parameters(parameters)
        cls._custom_params[exercise_type] = parameters

    @classmethod
    def get_threshold_down(cls, exercise_type: ExerciseType) -> float:
        """Pobierz próg dolny (pełne zgięcie)"""
        params = cls.get_parameters(exercise_type)
        return params.thresholds.threshold_down

    @classmethod
    def get_threshold_up(cls, exercise_type: ExerciseType) -> float:
        """Pobierz próg górny (pełny wyprost)"""
        params = cls.get_parameters(exercise_type)
        return params.thresholds.threshold_up

    @classmethod
    def get_cooldown(cls, exercise_type: ExerciseType) -> float:
        """Pobierz cooldown dla feedback'u"""
        params = cls.get_parameters(exercise_type)
        return params.feedback.cooldown_seconds

    @classmethod
    def get_custom_param(cls, exercise_type: ExerciseType,
                        param_name: str, default=None) -> Any:
        """Pobierz custom parametr"""
        params = cls.get_parameters(exercise_type)
        return params.custom_params.get(param_name, default)

    @classmethod
    def reset_to_defaults(cls) -> None:
        """Resetuj wszystkie custom parametry do domyślnych"""
        cls._custom_params.clear()

    @classmethod
    def get_all_parameters(cls, exercise_type: ExerciseType) -> Dict[str, Any]:
        """Pobierz wszystkie parametry jako słownik"""
        params = cls.get_parameters(exercise_type)
        return {
            "exercise_type": params.exercise_type.value,
            "threshold_down": params.thresholds.threshold_down,
            "threshold_up": params.thresholds.threshold_up,
            "cooldown_seconds": params.feedback.cooldown_seconds,
            "visibility_threshold": params.visibility.visibility_threshold,
            "use_fallback": params.visibility.use_fallback,
            **params.custom_params
        }


class ParameterPresets:
    """Predefiniowane zestawy parametrów dla różnych scenariuszy"""

    # Tryb łatwy - większa tolerancja
    SQUAT_EASY = ExerciseParameters(
        exercise_type=ExerciseType.SQUAT,
        thresholds=ExerciseThresholds(
            threshold_down=100.0,     # Mniej głębokie zgięcie
            threshold_up=150.0        # Mniej wymagające wyprost
        ),
        feedback=FeedbackSettings(cooldown_seconds=3.0),
        visibility=VisibilitySettings(visibility_threshold=0.3),
        custom_params={
            "min_angle_variance": 10.0,
            "stability_frames": 5,
        }
    )

    # Tryb zaawansowany - większa precyzja
    SQUAT_ADVANCED = ExerciseParameters(
        exercise_type=ExerciseType.SQUAT,
        thresholds=ExerciseThresholds(
            threshold_down=85.0,      # Głębokie zgięcie
            threshold_up=170.0        # Wymagające wyprost
        ),
        feedback=FeedbackSettings(cooldown_seconds=1.5),
        visibility=VisibilitySettings(visibility_threshold=0.5),
        custom_params={
            "min_angle_variance": 2.0,
            "stability_frames": 2,
        }
    )

    # Tryb łatwy dla pompek
    PUSHUP_EASY = ExerciseParameters(
        exercise_type=ExerciseType.PUSHUP,
        thresholds=ExerciseThresholds(
            threshold_down=100.0,
            threshold_up=150.0
        ),
        feedback=FeedbackSettings(cooldown_seconds=3.0),
        visibility=VisibilitySettings(visibility_threshold=0.3),
        custom_params={
            "arm_width_min": 0.8,
            "arm_width_max": 2.0,
            "body_alignment_tolerance": 30.0,
            "min_arm_symmetry": 0.7,
        }
    )

    # Tryb zaawansowany dla pompek
    PUSHUP_ADVANCED = ExerciseParameters(
        exercise_type=ExerciseType.PUSHUP,
        thresholds=ExerciseThresholds(
            threshold_down=85.0,
            threshold_up=170.0
        ),
        feedback=FeedbackSettings(cooldown_seconds=1.5),
        visibility=VisibilitySettings(visibility_threshold=0.5),
        custom_params={
            "arm_width_min": 1.0,
            "arm_width_max": 1.6,
            "body_alignment_tolerance": 15.0,
            "min_arm_symmetry": 0.9,
        }
    )

    @classmethod
    def get_preset(cls, preset_name: str) -> ExerciseParameters:
        """Pobierz preset parametrów"""
        presets = {
            "squat_easy": cls.SQUAT_EASY,
            "squat_advanced": cls.SQUAT_ADVANCED,
            "pushup_easy": cls.PUSHUP_EASY,
            "pushup_advanced": cls.PUSHUP_ADVANCED,
        }

        if preset_name not in presets:
            raise ValueError(
                f"Nieznany preset: {preset_name}. "
                f"Dostępne: {list(presets.keys())}"
            )

        return presets[preset_name]

    @classmethod
    def list_presets(cls) -> list:
        """Lista wszystkich dostępnych presetów"""
        return [
            "squat_easy",
            "squat_advanced",
            "pushup_easy",
            "pushup_advanced",
        ]


# Przykład użycia
if __name__ == "__main__":
    # Pobierz domyślne parametry dla przysiadów
    squat_params = ParametersManager.get_parameters(ExerciseType.SQUAT)
    print(f"Squat parameters: {squat_params}")

    # Pobierz konkretny parametr
    threshold_down = ParametersManager.get_threshold_down(ExerciseType.SQUAT)
    print(f"Squat threshold_down: {threshold_down}")

    # Użyj predefiniowanego presetu
    easy_preset = ParameterPresets.get_preset("squat_easy")
    ParametersManager.set_parameters(ExerciseType.SQUAT, easy_preset)
    print(f"Switched to easy mode: {ParametersManager.get_all_parameters(ExerciseType.SQUAT)}")

    # Wyświetl wszystkie dostępne presety
    print(f"Available presets: {ParameterPresets.list_presets()}")

