from dataclasses import dataclass

from app.food.catalog import FOODS, nutrients


@dataclass(frozen=True)
class Ingredient:
    slug: str
    grams: int


@dataclass(frozen=True)
class Recipe:
    name: str
    meal: str
    ingredients: tuple[Ingredient, ...]


I = Ingredient
R = Recipe
RECIPES = (
    R("Овсянка с творогом и бананом", "Завтрак", (I("oats_dry", 60), I("cottage5", 120), I("banana", 100))),
    R("Омлет с хлебом и овощами", "Завтрак", (I("egg", 120), I("bread", 70), I("tomato", 120), I("cucumber", 100))),
    R("Овсянка с соевым йогуртом и ягодами", "Завтрак", (I("oats_dry", 65), I("soy_yogurt", 180), I("berries", 100), I("nuts", 15))),
    R("Тофу с авокадо и хлебом", "Завтрак", (I("tofu", 150), I("avocado", 70), I("bread", 70), I("tomato", 100))),
    R("Курица с гречкой и салатом", "Обед", (I("chicken", 170), I("buckwheat", 220), I("tomato", 120), I("cucumber", 120), I("olive_oil", 10))),
    R("Индейка с рисом и овощами", "Обед", (I("turkey", 180), I("rice", 220), I("veg_mix", 180), I("olive_oil", 10))),
    R("Лосось с картофелем и брокколи", "Обед", (I("salmon", 160), I("potato", 260), I("broccoli", 180), I("olive_oil", 5))),
    R("Тофу с рисом и овощами", "Обед", (I("tofu", 220), I("rice", 220), I("veg_mix", 200), I("olive_oil", 10))),
    R("Творог с яблоком и орехами", "Перекус", (I("cottage5", 180), I("apple", 150), I("nuts", 15))),
    R("Йогурт с бананом и ягодами", "Перекус", (I("yogurt2", 220), I("banana", 100), I("berries", 80))),
    R("Соевый йогурт с бананом и орехами", "Перекус", (I("soy_yogurt", 220), I("banana", 100), I("nuts", 20))),
    R("Яйца с хлебом и огурцом", "Перекус", (I("egg", 120), I("bread", 50), I("cucumber", 150))),
    R("Треска с картофелем и овощами", "Ужин", (I("cod", 200), I("potato", 240), I("veg_mix", 200), I("olive_oil", 10))),
    R("Курица с пастой и брокколи", "Ужин", (I("chicken", 160), I("pasta", 200), I("broccoli", 180), I("olive_oil", 5))),
    R("Индейка с гречкой и салатом", "Ужин", (I("turkey", 180), I("buckwheat", 210), I("tomato", 120), I("cucumber", 120), I("olive_oil", 8))),
    R("Тофу с гречкой и брокколи", "Ужин", (I("tofu", 220), I("buckwheat", 220), I("broccoli", 180), I("olive_oil", 8))),
)
MEALS = ("Завтрак", "Обед", "Перекус", "Ужин")


def _eligible(recipe: Recipe, excluded: set[str]) -> bool:
    return not any(item.slug in excluded for item in recipe.ingredients)


def _recipe_values(recipe: Recipe, factor: float) -> dict:
    ingredients = []
    totals = {"kcal": 0, "protein": 0.0, "fat": 0.0, "carbs": 0.0, "fiber": 0.0}
    for item in recipe.ingredients:
        grams = max(60, round(item.grams * factor / 60) * 60) if item.slug == "egg" else max(1, round(item.grams * factor / 5) * 5)
        value = nutrients(item.slug, grams)
        for key in totals: totals[key] += value[key]
        food = FOODS[item.slug]
        amount = f"{grams} г"
        if item.slug == "egg": amount += f" (≈ {grams // 60} шт.)"
        ingredients.append(f"• {food.name}: {amount}")
    return {"name": recipe.name, "meal": recipe.meal, "ingredients": ingredients,
            "kcal": round(totals["kcal"]), "protein": round(totals["protein"]),
            "fat": round(totals["fat"]), "carbs": round(totals["carbs"]), "fiber": round(totals["fiber"])}


def build_day(target_kcal: int, day_index: int = 0, excluded: set[str] | None = None) -> list[dict]:
    if not 1200 <= target_kcal <= 5000: raise ValueError("Unsupported calorie target")
    excluded = excluded or set()
    selected = []
    for meal in MEALS:
        options = [recipe for recipe in RECIPES if recipe.meal == meal and _eligible(recipe, excluded)]
        if not options:
            raise ValueError(f"Не найден безопасный вариант для: {meal.lower()}")
        selected.append(options[day_index % len(options)])
    base = sum(_recipe_values(recipe, 1)["kcal"] for recipe in selected)
    factor = target_kcal / base
    return [_recipe_values(recipe, factor) for recipe in selected]


def format_day(target_kcal: int, day_index: int = 0, excluded: set[str] | None = None, compact: bool = False) -> str:
    meals = build_day(target_kcal, day_index, excluded)
    lines = [f"🍽 День {day_index + 1} · {sum(x['kcal'] for x in meals)} ккал"]
    for meal in meals:
        if compact:
            lines.append(f"• {meal['meal']}: {meal['name']} — {meal['kcal']} ккал")
        else:
            lines.extend((f"\n{meal['meal']} — {meal['name']}", *meal["ingredients"],
                          f"Итого: {meal['kcal']} ккал · Б {meal['protein']} · Ж {meal['fat']} · У {meal['carbs']}"))
    lines.append("\nВес круп и гарниров указан в состоянии из названия продукта. Проверяйте состав и аллергены на этикетке.")
    return "\n".join(lines)


def format_week(target_kcal: int, excluded: set[str] | None = None) -> str:
    return "\n\n".join(format_day(target_kcal, index, excluded, compact=True) for index in range(7))
