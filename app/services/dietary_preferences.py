from app.food.catalog import FOODS


ALIASES = {
    "рыб": {"salmon", "cod"}, "лосос": {"salmon"}, "треск": {"cod"},
    "лактоз": {"cottage5", "yogurt2", "kefir1"}, "молоч": {"cottage5", "yogurt2", "kefir1"},
    "творог": {"cottage5"}, "йогурт": {"yogurt2"}, "кефир": {"kefir1"},
    "яблок": {"apple"}, "банан": {"banana"}, "яйц": {"egg"},
    "куриц": {"chicken"}, "индейк": {"turkey"}, "орех": {"nuts"},
    "глютен": {"oats_dry", "bread", "pasta"},
}


def parse_exclusions(text: str) -> list[str]:
    lowered = text.lower().replace("ё", "е")
    excluded: set[str] = set()
    if lowered.strip() in {"нет", "ничего", "-", "без ограничений"}:
        return []
    for fragment, slugs in ALIASES.items():
        if fragment in lowered:
            excluded.update(slugs)
    for slug, food in FOODS.items():
        if food.name.lower().split(",")[0] in lowered:
            excluded.add(slug)
    return sorted(excluded)
