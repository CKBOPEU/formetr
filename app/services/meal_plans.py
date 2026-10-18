from dataclasses import dataclass


@dataclass(frozen=True)
class Meal:
    name: str
    base_kcal: int
    protein: float
    fat: float
    carbs: float
    ingredients: str


DAYS = (
    (Meal("Овсянка с творогом и бананом", 430, 27, 10, 59, "овсянка, творог, банан"), Meal("Курица с гречкой и овощами", 570, 48, 15, 61, "курица, гречка, овощи, масло"), Meal("Йогурт с яблоком и орехами", 270, 13, 12, 31, "йогурт, яблоко, орехи"), Meal("Рыба с картофелем и брокколи", 480, 38, 15, 49, "рыба, картофель, брокколи")),
    (Meal("Омлет и цельнозерновой хлеб", 420, 25, 19, 37, "яйца, хлеб, овощи"), Meal("Индейка с рисом и салатом", 560, 45, 14, 64, "индейка, рис, овощи, масло"), Meal("Творог с ягодами", 260, 27, 9, 20, "творог, ягоды"), Meal("Паста с курицей и овощами", 510, 40, 12, 61, "макароны, курица, овощи")),
    (Meal("Творог, овсянка и ягоды", 410, 31, 11, 49, "творог, овсянка, ягоды"), Meal("Рыба с рисом и овощами", 550, 38, 18, 58, "рыба, рис, овощи"), Meal("Кефир, банан и орехи", 280, 11, 11, 37, "кефир, банан, орехи"), Meal("Индейка с гречкой и салатом", 500, 43, 13, 54, "индейка, гречка, овощи")),
    (Meal("Овсянка с йогуртом и яблоком", 400, 20, 9, 61, "овсянка, йогурт, яблоко"), Meal("Курица с пастой и брокколи", 580, 48, 14, 66, "курица, макароны, брокколи"), Meal("Творог и банан", 290, 25, 7, 34, "творог, банан"), Meal("Треска с картофелем и салатом", 450, 39, 11, 48, "треска, картофель, овощи, масло")),
    (Meal("Яйца, авокадо и хлеб", 440, 23, 23, 35, "яйца, авокадо, хлеб"), Meal("Индейка с гречкой", 540, 46, 14, 57, "индейка, гречка, овощи"), Meal("Йогурт с ягодами и орехами", 280, 14, 13, 27, "йогурт, ягоды, орехи"), Meal("Курица с рисом и овощами", 500, 42, 11, 59, "курица, рис, овощи")),
    (Meal("Овсянка с бананом и орехами", 430, 15, 14, 65, "овсянка, банан, орехи"), Meal("Лосось с картофелем", 590, 39, 25, 49, "лосось, картофель, овощи"), Meal("Творог с яблоком", 260, 26, 8, 24, "творог, яблоко"), Meal("Индейка с пастой и салатом", 490, 41, 11, 57, "индейка, макароны, овощи")),
    (Meal("Омлет с овощами и хлебом", 410, 26, 18, 36, "яйца, овощи, хлеб"), Meal("Курица с рисом и брокколи", 550, 47, 12, 63, "курица, рис, брокколи"), Meal("Кефир, ягоды и орехи", 270, 11, 13, 28, "кефир, ягоды, орехи"), Meal("Треска с гречкой и салатом", 470, 40, 11, 51, "треска, гречка, овощи")),
)

MEAL_LABELS = ("Завтрак", "Обед", "Перекус", "Ужин")


def build_day(target_kcal: int, day_index: int = 0) -> list[dict]:
    if not 1200 <= target_kcal <= 5000:
        raise ValueError("Unsupported calorie target")
    template = DAYS[day_index % len(DAYS)]
    factor = target_kcal / sum(meal.base_kcal for meal in template)
    return [{
        "label": label,
        "name": meal.name,
        "kcal": round(meal.base_kcal * factor),
        "protein": round(meal.protein * factor),
        "fat": round(meal.fat * factor),
        "carbs": round(meal.carbs * factor),
        "portion_percent": round(factor * 100),
        "ingredients": meal.ingredients,
    } for label, meal in zip(MEAL_LABELS, template)]


def format_day(target_kcal: int, day_index: int = 0, compact: bool = False) -> str:
    meals = build_day(target_kcal, day_index)
    lines = [f"🍽 День {day_index + 1} · около {sum(x['kcal'] for x in meals)} ккал"]
    for meal in meals:
        if compact:
            lines.append(f"• {meal['label']}: {meal['name']} — {meal['kcal']} ккал")
        else:
            lines.extend((f"\n{meal['label']} — {meal['name']}", f"{meal['kcal']} ккал · Б {meal['protein']} · Ж {meal['fat']} · У {meal['carbs']}", f"Состав: {meal['ingredients']} · порция {meal['portion_percent']}% от базовой"))
    lines.append("\nКоличество ингредиентов масштабируется пропорционально. Учитывайте этикетки конкретных продуктов.")
    return "\n".join(lines)


def format_week(target_kcal: int) -> str:
    return "\n\n".join(format_day(target_kcal, index, compact=True) for index in range(7))
