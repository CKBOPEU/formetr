from app.calculations.safety import needs_medical_review
from app.exercises.catalog import CATALOG
from app.services.plans import generate_plan


def test_any_reported_medical_condition_disables_standard_algorithm() -> None:
    assert needs_medical_review("астма")
    assert not needs_medical_review(None)


def test_every_home_exercise_is_available_at_home() -> None:
    plan = generate_plan(4, "intermediate", "home", "maintain")
    assert all("home" in CATALOG[item["slug"]].equipment for day in plan["days"] for item in day["exercises"])


def test_named_limitation_removes_exercise() -> None:
    plan = generate_plan(2, "beginner", "gym", "maintain", limitations="Гоблет-присед")
    names = {item["name"] for day in plan["days"] for item in day["exercises"]}
    assert "Гоблет-присед" not in names
