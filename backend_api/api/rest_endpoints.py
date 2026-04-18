from fastapi import APIRouter, HTTPException, Request

router = APIRouter()


# 1. Lista ćwiczeń - to zasila menu główne w React
@router.get("/exercises", tags=["Content"])
async def get_exercises():
    """Zwraca listę dostępnych ćwiczeń, które nasz silnik potrafi analizować."""
    return [
        {
            "id": "squat",
            "name": "Przysiady",
            "difficulty": "Łatwe",
            "thumbnail": "https://img.icons8.com/color/96/squats.png"
        },
        {
            "id": "pushup",
            "name": "Pompki",
            "difficulty": "Średnie",
            "thumbnail": "https://img.icons8.com/color/96/pushups.png"
        }
    ]


# 2. Szczegóły ćwiczenia - GIFy i instrukcje (Twój most do bazy wiedzy)
@router.get("/exercises/{exercise_id}", tags=["Content"])
async def get_exercise_details(exercise_id: str):
    """Pobiera instrukcję i GIF-a instruktażowego przed startem kamery."""

    # Przykładowa baza danych wewnątrz pliku (później przeniesiesz to do services/exercise_db.py)
    exercise_data = {
        "squat": {
            "name": "Przysiady",
            "gif_url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJndXh6bm5xeXp4ZzR6eXp4ZzR6eXp4ZzR6eXp4ZzR6eXp4ZzR6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKu57TXYNoiOvxK/giphy.gif",
            "instruction": "Ustaw stopy na szerokość barków. Schodź nisko, trzymając proste plecy.",
            "target_angle": 90
        },
        "pushup": {
            "name": "Pompki",
            "gif_url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJndXh6bm5xeXp4ZzR6eXp4ZzR6eXp4ZzR6eXp4ZzR6eXp4ZzR6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/26vIfmXN6m99fD1Y4/giphy.gif",
            "instruction": "Ciało w linii prostej. Opuszczaj klatkę tuż nad podłogę.",
            "target_angle": 160
        }
    }

    data = exercise_data.get(exercise_id)
    if not data:
        raise HTTPException(status_code=404, detail="Nie znaleziono takiego ćwiczenia")

    return data


# 3. Health Check - sprawdzamy tylko czy model AI żyje
@router.get("/status", tags=["System"])
async def get_system_status(request: Request):
    """Sprawdza stan silnika wizyjnego (Osoba 1)."""
    pose_ready = hasattr(request.app.state, "pose_engine")
    return {
        "status": "online",
        "vision_engine": "READY" if pose_ready else "INITIALIZING",
        "java_bridge": "DISABLED"  # Informacja, że Java jest obecnie wyłączona
    }