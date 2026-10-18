from app.calculations.safety import needs_medical_review


def test_medical_marker() -> None:
    assert needs_medical_review("Есть беременность")
    assert not needs_medical_review("нет")
