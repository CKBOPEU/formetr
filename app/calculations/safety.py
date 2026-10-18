MEDICAL_MARKERS = ("беремен", "рпп", "анорекс", "булим", "диабет", "болезн", "травм", "врач")


def needs_medical_review(text: str | None) -> bool:
    normalized = (text or "").lower()
    if normalized.strip() in {"", "нет", "no", "none"}:
        return False
    return True
