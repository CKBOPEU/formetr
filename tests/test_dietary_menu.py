from app.services.assistant import answer_question
from app.services.dietary_preferences import parse_exclusions
from app.services.meal_plans_v2 import build_day, format_day


def test_natural_language_exclusions_are_recognized() -> None:
    excluded = set(parse_exclusions("Не ем рыбу и яблоки, непереносимость лактозы"))
    assert {"salmon", "cod", "apple", "cottage5", "yogurt2", "kefir1"} <= excluded


def test_menu_avoids_excluded_foods() -> None:
    excluded = {"salmon", "cod", "cottage5", "yogurt2", "kefir1", "apple"}
    meals = build_day(1900, excluded=excluded)
    rendered = " ".join(meal["name"] + " " + " ".join(meal["ingredients"]) for meal in meals).lower()
    assert "лосось" not in rendered
    assert "треска" not in rendered
    assert "творог" not in rendered
    assert "яблоко" not in rendered


def test_recipe_lists_exact_grams_and_egg_units() -> None:
    text = format_day(1800, day_index=1)
    assert " г" in text
    assert "шт." in text
    assert "." not in text.split("шт.")[0].split("≈ ")[-1]


def test_assistant_uses_personal_calorie_target() -> None:
    answer = answer_question("Сколько мне калорий?", 1850, "maintain", 2)
    assert "1850" in answer
