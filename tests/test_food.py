import pytest

from app.food.catalog import nutrients
from app.bot.handlers_food import food_card, food_list
from app.services.meal_plans import build_day, format_week


def test_food_portion_scales_nutrients() -> None:
    assert nutrients("chicken", 200) == {
        "kcal": 330, "protein": 62.0, "fat": 7.2, "carbs": 0.0, "fiber": 0.0,
    }


def test_food_portion_rejects_unsafe_values() -> None:
    with pytest.raises(ValueError):
        nutrients("chicken", 0)


def test_day_menu_matches_target_with_rounding() -> None:
    meals = build_day(1850)
    assert len(meals) == 4
    assert abs(sum(meal["kcal"] for meal in meals) - 1850) <= 2
    assert all(meal["protein"] > 0 for meal in meals)


def test_week_menu_contains_seven_days() -> None:
    text = format_week(1850)
    assert sum(f"День {day}" in text for day in range(1, 8)) == 7


def test_deep_food_screens_have_home_navigation() -> None:
    _, card = food_card("chicken")
    category = food_list("protein")
    for keyboard in (card, category):
        callbacks = [button.callback_data for row in keyboard.inline_keyboard for button in row]
        assert "menu:home" in callbacks
