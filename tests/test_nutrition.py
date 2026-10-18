import pytest
from app.calculations.nutrition import calculate_bmr, calculate_targets


def test_mifflin_male() -> None:
    assert calculate_bmr("male", 30, 180, 80) == 1780


def test_mifflin_female() -> None:
    assert calculate_bmr("female", 30, 165, 60) == pytest.approx(1320.25)


def test_minor_is_rejected() -> None:
    with pytest.raises(ValueError): calculate_bmr("female", 17, 165, 60)


def test_calorie_floor_and_macros() -> None:
    result = calculate_targets(sex="female", age=40, height_cm=150, weight_kg=45, activity="low", goal="fat_loss")
    assert result.calories >= 1200
    assert result.protein_min < result.protein_max
    assert result.fiber >= 25
