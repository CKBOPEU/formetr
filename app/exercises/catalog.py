from dataclasses import dataclass


@dataclass(frozen=True)
class ExerciseDefinition:
    slug: str
    name: str
    primary: tuple[str, ...]
    secondary: tuple[str, ...]
    kind: str
    equipment: tuple[str, ...]
    difficulty: str
    reps: tuple[int, int]
    alternatives: tuple[str, ...] = ()


E = ExerciseDefinition
CATALOG = {
    x.slug: x for x in (
        E("goblet_squat", "Гоблет-присед", ("quadriceps", "glutes"), ("core",), "compound", ("home", "minimal", "gym"), "beginner", (8, 12), ("leg_press",)),
        E("leg_press", "Жим ногами", ("quadriceps", "glutes"), ("hamstrings",), "compound", ("gym",), "beginner", (8, 12), ("goblet_squat",)),
        E("romanian_deadlift", "Румынская тяга", ("hamstrings", "glutes"), ("back",), "compound", ("gym", "minimal"), "intermediate", (6, 10), ("hip_hinge",)),
        E("hip_hinge", "Наклон-тазобедренный шарнир", ("hamstrings", "glutes"), ("back",), "compound", ("home",), "beginner", (10, 15), ("romanian_deadlift",)),
        E("hip_thrust", "Ягодичный мост", ("glutes",), ("hamstrings",), "compound", ("home", "minimal", "gym"), "beginner", (8, 15)),
        E("reverse_lunge", "Обратные выпады", ("glutes", "quadriceps"), ("core",), "compound", ("home", "minimal", "gym"), "intermediate", (8, 12)),
        E("calf_raise", "Подъёмы на носки", ("calves",), (), "isolation", ("home", "minimal", "gym"), "beginner", (10, 15)),
        E("push_up", "Отжимания", ("chest",), ("triceps", "shoulders"), "compound", ("home", "minimal", "gym"), "beginner", (6, 15), ("dumbbell_press",)),
        E("dumbbell_press", "Жим гантелей лёжа", ("chest",), ("triceps", "shoulders"), "compound", ("minimal", "gym"), "beginner", (8, 12), ("push_up",)),
        E("overhead_press", "Жим над головой", ("shoulders",), ("triceps",), "compound", ("minimal", "gym"), "intermediate", (6, 10), ("pike_push_up",)),
        E("pike_push_up", "Отжимания уголком", ("shoulders",), ("triceps",), "compound", ("home",), "intermediate", (6, 12), ("overhead_press",)),
        E("lat_pulldown", "Тяга верхнего блока", ("lats",), ("biceps",), "compound", ("gym",), "beginner", (8, 12), ("band_pulldown",)),
        E("band_pulldown", "Тяга резины сверху", ("lats",), ("biceps",), "compound", ("minimal", "home"), "beginner", (10, 15), ("lat_pulldown",)),
        E("seated_row", "Горизонтальная тяга", ("back",), ("biceps", "rear_delts"), "compound", ("gym",), "beginner", (8, 12), ("one_arm_row",)),
        E("one_arm_row", "Тяга гантели одной рукой", ("back",), ("biceps", "rear_delts"), "compound", ("minimal", "gym"), "beginner", (8, 12), ("seated_row",)),
        E("band_row", "Тяга резины к поясу", ("back",), ("biceps",), "compound", ("home", "minimal"), "beginner", (10, 15), ("seated_row",)),
        E("lateral_raise", "Разведения в стороны", ("shoulders",), (), "isolation", ("minimal", "gym"), "beginner", (10, 15)),
        E("biceps_curl", "Сгибание на бицепс", ("biceps",), ("forearms",), "isolation", ("minimal", "gym"), "beginner", (8, 15), ("towel_curl",)),
        E("towel_curl", "Изометрическое сгибание с полотенцем", ("biceps",), ("forearms",), "isolation", ("home",), "beginner", (20, 40), ("biceps_curl",)),
        E("triceps_pushdown", "Разгибание рук на блоке", ("triceps",), (), "isolation", ("gym",), "beginner", (8, 15), ("band_triceps",)),
        E("band_triceps", "Разгибание рук с резиной", ("triceps",), (), "isolation", ("minimal", "home"), "beginner", (10, 15), ("triceps_pushdown",)),
        E("dead_bug", "Dead bug", ("core",), (), "stability", ("home", "minimal", "gym"), "beginner", (8, 12)),
        E("plank", "Планка", ("core",), ("shoulders",), "stability", ("home", "minimal", "gym"), "beginner", (20, 40)),
    )
}
