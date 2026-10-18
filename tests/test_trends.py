from app.calculations.trends import calculate_trend, review_progress


def test_requires_multiple_weeks() -> None:
    assert calculate_trend([60, 59]) is None


def test_four_week_trend() -> None:
    trend = calculate_trend([62.0, 61.7, 61.2, 60.9])
    assert trend is not None
    assert trend.change < 0


def test_stalled_loss_proposes_change() -> None:
    decision, _, percent = review_progress([70, 70.1, 70.0, 70.2], "fat_loss")
    assert decision == "propose"
    assert percent == -5
