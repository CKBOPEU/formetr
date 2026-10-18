from dataclasses import dataclass
from statistics import mean


@dataclass(frozen=True)
class Trend:
    first_average: float
    last_average: float
    change: float
    weekly_rate: float


def calculate_trend(values: list[float]) -> Trend | None:
    if len(values) < 3:
        return None
    window = min(2, len(values) // 2)
    first, last = mean(values[:window]), mean(values[-window:])
    change = last - first
    return Trend(round(first, 2), round(last, 2), round(change, 2), round(change / max(1, len(values) - window), 2))


def review_progress(weights: list[float], goal: str) -> tuple[str, str, int]:
    trend = calculate_trend(weights)
    if trend is None:
        return "wait", "Для решения нужно минимум три еженедельных измерения.", 0
    relative = trend.change / trend.first_average
    if goal in {"fat_loss", "reduce_area"}:
        if relative > -0.005:
            return "propose", "Средний вес не снижается несколько недель; можно уменьшить рацион на 5%.", -5
        if relative < -0.04:
            return "propose", "Темп снижения слишком высокий; можно увеличить рацион на 5%.", 5
    if goal == "muscle_gain" and relative < 0.002:
        return "propose", "Устойчивого роста среднего веса нет; можно увеличить рацион на 5%.", 5
    return "keep", "Динамика соответствует цели. План пока менять не нужно.", 0
