from app.services.plans import generate_plan


def test_generates_all_supported_splits() -> None:
    for days in (2, 3, 4):
        plan = generate_plan(days, "beginner", "gym", "maintain")
        assert len(plan["days"]) == days
        assert all(day["exercises"] for day in plan["days"])


def test_home_plan_uses_home_exercises() -> None:
    plan = generate_plan(3, "beginner", "home", "maintain")
    assert plan["days_per_week"] == 3


def test_quad_reduction_lowers_direct_sets() -> None:
    normal = generate_plan(2, "intermediate", "gym", "maintain")
    reduced = generate_plan(2, "intermediate", "gym", "reduce_area", "thigh")
    normal_quad = sum(x["sets"] for d in normal["days"] for x in d["exercises"] if x["slug"] in {"goblet_squat", "leg_press", "reverse_lunge"})
    reduced_quad = sum(x["sets"] for d in reduced["days"] for x in d["exercises"] if x["slug"] in {"goblet_squat", "leg_press", "reverse_lunge"})
    assert reduced_quad < normal_quad
