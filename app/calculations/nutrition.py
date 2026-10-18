from dataclasses import dataclass

ACTIVITY_FACTORS = {"low": 1.2, "light": 1.375, "moderate": 1.55, "high": 1.725}
GOAL_FACTORS = {"fat_loss": 0.85, "maintain": 1.0, "muscle_gain": 1.08, "recomposition": 0.95, "reduce_area": 0.9}
CALORIE_FLOORS = {"female": 1200, "male": 1500}


@dataclass(frozen=True)
class NutritionResult:
    bmr: int
    tdee: int
    calories: int
    protein_min: int
    protein_max: int
    fat_min: int
    fat_max: int
    carbs: int
    fiber: int


def calculate_bmr(sex: str, age: int, height_cm: float, weight_kg: float) -> float:
    if age < 18:
        raise ValueError("Adult formula is not used for minors")
    if sex not in {"male", "female"}:
        raise ValueError("sex must be male or female")
    offset = 5 if sex == "male" else -161
    return 10 * weight_kg + 6.25 * height_cm - 5 * age + offset


def calculate_targets(*, sex: str, age: int, height_cm: float, weight_kg: float, activity: str, goal: str) -> NutritionResult:
    bmr = calculate_bmr(sex, age, height_cm, weight_kg)
    if activity not in ACTIVITY_FACTORS or goal not in GOAL_FACTORS:
        raise ValueError("Unknown activity or goal")
    tdee = bmr * ACTIVITY_FACTORS[activity]
    planned = tdee * GOAL_FACTORS[goal]
    floor = max(CALORIE_FLOORS[sex], bmr * 0.9)
    calories = round(max(planned, floor) / 10) * 10
    protein_factor = (1.6, 2.0) if goal in {"fat_loss", "recomposition", "reduce_area"} else (1.4, 1.8)
    protein_min, protein_max = (round(weight_kg * x) for x in protein_factor)
    fat_min, fat_max = round(weight_kg * 0.8), round(weight_kg * 1.0)
    carbs = max(0, round((calories - protein_min * 4 - fat_min * 9) / 4))
    fiber = max(25, round(calories / 1000 * 14))
    return NutritionResult(round(bmr), round(tdee), calories, protein_min, protein_max, fat_min, fat_max, carbs, fiber)
