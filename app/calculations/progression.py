from dataclasses import dataclass


@dataclass(frozen=True)
class ProgressionAdvice:
    action: str
    message: str


def advise_progression(reps: list[int], rep_min: int, rep_max: int, rir: float, technique_good: bool = True) -> ProgressionAdvice:
    if not reps:
        raise ValueError("At least one set is required")
    if any(rep < rep_min for rep in reps) or rir < 1:
        return ProgressionAdvice("decrease", "Снизьте вес на 5–10% и вернитесь в заданный диапазон с чистой техникой.")
    if all(rep >= rep_max for rep in reps) and 1.5 <= rir <= 3 and technique_good:
        return ProgressionAdvice("increase", "На следующей тренировке немного увеличьте нагрузку: 1–2 кг для верхней части или 2,5–5 кг для нижней.")
    return ProgressionAdvice("keep", "Оставьте вес и постарайтесь добавить повторение, сохраняя заданный RIR.")
