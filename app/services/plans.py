from dataclasses import asdict, dataclass
from app.exercises.catalog import CATALOG

TARGET_MUSCLES = {
    "arms": {"biceps", "triceps"}, "shoulders": {"shoulders", "rear_delts"},
    "thigh": {"quadriceps"}, "glutes": {"glutes"}, "calves": {"calves"}, "other": set(),
}
TEMPLATES = {
    2: [["goblet_squat", "romanian_deadlift", "dumbbell_press", "lat_pulldown", "dead_bug"],
        ["hip_thrust", "reverse_lunge", "seated_row", "overhead_press", "plank"]],
    3: [["goblet_squat", "dumbbell_press", "lat_pulldown", "dead_bug"],
        ["romanian_deadlift", "hip_thrust", "overhead_press", "seated_row"],
        ["reverse_lunge", "dumbbell_press", "one_arm_row", "lateral_raise", "plank"]],
    4: [["goblet_squat", "romanian_deadlift", "calf_raise", "dead_bug"],
        ["dumbbell_press", "lat_pulldown", "lateral_raise", "biceps_curl"],
        ["hip_thrust", "reverse_lunge", "calf_raise", "plank"],
        ["overhead_press", "seated_row", "dumbbell_press", "triceps_pushdown"]],
}


@dataclass(frozen=True)
class PlannedExercise:
    slug: str
    name: str
    sets: int
    rep_min: int
    rep_max: int
    rir: str
    rest_seconds: int


def _available(slug: str, equipment: str) -> str:
    exercise = CATALOG[slug]
    if equipment in exercise.equipment:
        return slug
    for alternative in exercise.alternatives:
        if equipment in CATALOG[alternative].equipment:
            return alternative
    candidates = [x.slug for x in CATALOG.values() if equipment in x.equipment and x.primary[0] == exercise.primary[0]]
    return candidates[0] if candidates else slug


def generate_plan(days: int, experience: str, equipment: str, goal: str, target_area: str | None = None, limitations: str | None = None) -> dict:
    if days not in TEMPLATES:
        raise ValueError("MVP supports 2, 3 or 4 training days")
    reduced = TARGET_MUSCLES.get(target_area or "", set()) if goal == "reduce_area" else set()
    base_sets = {"beginner": 2, "intermediate": 3, "advanced": 3}.get(experience, 2)
    blocked = (limitations or "").lower()
    result = []
    for number, template in enumerate(TEMPLATES[days], 1):
        exercises = []
        for original in template:
            slug = _available(original, equipment)
            item = CATALOG[slug]
            if blocked and (item.name.lower() in blocked or item.slug.replace("_", " ") in blocked):
                alternatives = [candidate for candidate in item.alternatives if equipment in CATALOG[candidate].equipment and CATALOG[candidate].name.lower() not in blocked]
                if not alternatives:
                    continue
                slug = alternatives[0]
                item = CATALOG[slug]
            if equipment not in item.equipment:
                continue
            direct_reduced = bool(set(item.primary) & reduced)
            indirect_reduced = bool(set(item.secondary) & reduced)
            if direct_reduced and item.kind == "isolation":
                continue
            sets = 1 if direct_reduced else max(2, base_sets - (1 if indirect_reduced else 0))
            rest = 120 if item.kind == "compound" else 75
            exercises.append(asdict(PlannedExercise(slug, item.name, sets, *item.reps, "2–3", rest)))
        result.append({"day": number, "exercises": exercises})
    return {"days_per_week": days, "days": result, "target_volume_reduced": sorted(reduced)}


def replace_exercise(plan: dict, day_number: int, slug: str, equipment: str) -> dict:
    day = plan["days"][day_number - 1]
    current = CATALOG[slug]
    options = [x for x in current.alternatives if equipment in CATALOG[x].equipment]
    if not options:
        options = [x.slug for x in CATALOG.values() if x.slug != slug and equipment in x.equipment and set(x.primary) & set(current.primary)]
    if not options:
        return plan
    replacement = CATALOG[options[0]]
    for item in day["exercises"]:
        if item["slug"] == slug:
            item.update(slug=replacement.slug, name=replacement.name, rep_min=replacement.reps[0], rep_max=replacement.reps[1])
            break
    return plan
