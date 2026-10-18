from app.calculations.progression import advise_progression


def test_increase_after_top_range() -> None:
    assert advise_progression([12, 12, 12], 8, 12, 2).action == "increase"


def test_decrease_below_range() -> None:
    assert advise_progression([8, 7, 6], 8, 12, 1).action == "decrease"


def test_keep_in_middle() -> None:
    assert advise_progression([10, 10, 9], 8, 12, 2).action == "keep"
