GOAL_NAMES = {"fat_loss": "Снижение жировой массы", "maintain": "Поддержание формы", "muscle_gain": "Набор мышечной массы", "recomposition": "Улучшение композиции тела", "reduce_area": "Уменьшение выбранного обхвата"}
AREA_NAMES = {"arms": "руки", "shoulders": "плечи", "thigh": "бедро/квадрицепс", "glutes": "ягодицы", "calves": "икры", "other": "другая область"}


def format_plan(goal, nutrition, plan: dict, minor: bool = False, medical: bool = False) -> str:
    lines = [f"🎯 Цель\n{GOAL_NAMES.get(goal.kind, goal.kind)}" + (f": {AREA_NAMES.get(goal.target_area, goal.target_area)}" if goal.target_area else "")]
    if goal.kind == "reduce_area":
        lines.append("Локальное жиросжигание невозможно. План управляет общей жировой массой и снижает прямой и косвенный стимул выбранных мышц.")
    if minor:
        lines.append("⚠️ До 18 лет FORMETR не создаёт дефицит калорий или программу похудения. Изменение массы и питания обсудите с родителем/опекуном и медицинским специалистом.")
    elif medical:
        lines.append("⚠️ Обычный алгоритм изменения веса отключён. Получите персональную рекомендацию квалифицированного медицинского специалиста.")
    elif nutrition:
        lines.append(f"🥗 Питание\n{nutrition.calories} ккал\nБелок: {nutrition.protein_min}–{nutrition.protein_max} г\nЖиры: {nutrition.fat_min}–{nutrition.fat_max} г\nУглеводы: около {nutrition.carbs} г\nКлетчатка: {nutrition.fiber}+ г")
        lines.append("Это расчётная отправная точка, а не медицинское назначение. Оценивать её нужно по средним данным за несколько недель.")
    lines.append(f"🏋️ Тренировки: {plan['days_per_week']} раза в неделю")
    for day in plan["days"]:
        lines.append(f"\nДень {day['day']}")
        for x in day["exercises"]:
            lines.append(f"• {x['name']} → {x['sets']} × {x['rep_min']}–{x['rep_max']} → RIR {x['rir']} → отдых {x['rest_seconds']} сек")
    return "\n".join(lines)
