from dataclasses import dataclass


@dataclass(frozen=True)
class Food:
    slug: str
    name: str
    category: str
    kcal: float
    protein: float
    fat: float
    carbs: float
    fiber: float
    note: str = ""


F = Food
FOODS = {item.slug: item for item in (
    F("chicken", "Куриная грудка, готовая", "protein", 165, 31, 3.6, 0, 0),
    F("turkey", "Филе индейки, готовое", "protein", 150, 29, 3, 0, 0),
    F("salmon", "Лосось, готовый", "protein", 208, 20, 13, 0, 0),
    F("cod", "Треска, готовая", "protein", 105, 23, 0.9, 0, 0),
    F("egg", "Яйцо куриное", "protein", 157, 12.7, 11.5, 0.7, 0),
    F("cottage5", "Творог 5%", "dairy", 145, 17, 5, 3, 0),
    F("yogurt2", "Йогурт натуральный 2%", "dairy", 73, 5, 2, 7.5, 0),
    F("kefir1", "Кефир 1%", "dairy", 40, 3, 1, 4, 0),
    F("soy_yogurt", "Йогурт соевый без сахара", "dairy", 54, 4, 2.3, 4, 0.6),
    F("tofu", "Тофу", "protein", 120, 13, 7, 1.5, 1),
    F("oats_dry", "Овсяные хлопья, сухие", "grains", 366, 12.3, 6.1, 59.5, 8),
    F("buckwheat", "Гречка, варёная", "grains", 110, 4.2, 1.1, 21.3, 2.7),
    F("rice", "Рис, варёный", "grains", 130, 2.7, 0.3, 28, 0.4),
    F("pasta", "Макароны, варёные", "grains", 150, 5, 1.1, 30.9, 1.8),
    F("potato", "Картофель, варёный", "grains", 82, 2, 0.4, 16.7, 1.4),
    F("bread", "Хлеб цельнозерновой", "grains", 247, 13, 4.2, 41, 7),
    F("tomato", "Помидор", "vegetables", 18, 0.9, 0.2, 3.9, 1.2),
    F("cucumber", "Огурец", "vegetables", 15, 0.7, 0.1, 3.6, 0.5),
    F("broccoli", "Брокколи", "vegetables", 35, 2.4, 0.4, 7.2, 3.3),
    F("veg_mix", "Овощная смесь без соуса", "vegetables", 55, 2.5, 0.5, 10, 3),
    F("banana", "Банан", "fruit", 89, 1.1, 0.3, 22.8, 2.6),
    F("apple", "Яблоко", "fruit", 52, 0.3, 0.2, 13.8, 2.4),
    F("berries", "Ягоды", "fruit", 50, 1, 0.5, 10, 4),
    F("nuts", "Орехи, смесь", "fats", 607, 20, 54, 21, 7),
    F("olive_oil", "Оливковое масло", "fats", 884, 0, 100, 0, 0),
    F("avocado", "Авокадо", "fats", 160, 2, 14.7, 8.5, 6.7),
)}

CATEGORY_NAMES = {
    "protein": "🥩 Мясо, рыба и яйца",
    "dairy": "🥛 Молочные продукты",
    "grains": "🌾 Крупы и гарниры",
    "vegetables": "🥦 Овощи",
    "fruit": "🍎 Фрукты и ягоды",
    "fats": "🥜 Жиры и орехи",
}


def nutrients(slug: str, grams: float) -> dict[str, float]:
    if slug not in FOODS or not 1 <= grams <= 3000:
        raise ValueError("Unknown food or invalid serving")
    food = FOODS[slug]
    factor = grams / 100
    return {
        "kcal": round(food.kcal * factor),
        "protein": round(food.protein * factor, 1),
        "fat": round(food.fat * factor, 1),
        "carbs": round(food.carbs * factor, 1),
        "fiber": round(food.fiber * factor, 1),
    }
