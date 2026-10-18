from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.bot.handlers import router
from app.bot.states import DietarySettings, FoodLookup
from app.database.repositories import get_dashboard, get_dietary_preferences, save_dietary_preferences
from app.food.catalog import CATEGORY_NAMES, FOODS, nutrients
from app.services.dietary_preferences import parse_exclusions
from app.services.meal_plans_v2 import format_day, format_week


def food_home() -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=name, callback_data=f"foodcat:{slug}")] for slug, name in CATEGORY_NAMES.items()]
    rows.extend((
        [InlineKeyboardButton(text="🔍 Найти продукт", callback_data="food:search")],
        [InlineKeyboardButton(text="← Меню", callback_data="menu:home")],
    ))
    return InlineKeyboardMarkup(inline_keyboard=rows)


def food_list(category: str) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=item.name, callback_data=f"food:{item.slug}")] for item in FOODS.values() if item.category == category]
    rows.append([InlineKeyboardButton(text="← Категории", callback_data="menu:foods")])
    rows.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu:home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def food_card(slug: str, grams: int = 100) -> tuple[str, InlineKeyboardMarkup]:
    food = FOODS[slug]
    value = nutrients(slug, grams)
    text = (f"🔎 {food.name}\nПорция: {grams} г\n\n{value['kcal']} ккал\n"
            f"Белки: {value['protein']} г\nЖиры: {value['fat']} г\n"
            f"Углеводы: {value['carbs']} г\nКлетчатка: {value['fiber']} г\n\n"
            "Значения ориентировочные: проверяйте этикетку конкретного продукта.")
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{amount} г", callback_data=f"portion:{slug}:{amount}") for amount in (50, 100, 150)],
        [InlineKeyboardButton(text="200 г", callback_data=f"portion:{slug}:200"), InlineKeyboardButton(text="✏️ Своя порция", callback_data=f"portion_custom:{slug}")],
        [InlineKeyboardButton(text="← Каталог", callback_data=f"foodcat:{food.category}")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu:home")],
    ])
    return text, markup


@router.callback_query(F.data == "menu:foods")
async def show_foods(call: CallbackQuery) -> None:
    await call.answer()
    await call.message.answer("🔎 Каталог продуктов\nВсе значения указаны на 100 г, затем можно выбрать свою порцию.", reply_markup=food_home())


@router.callback_query(F.data.startswith("foodcat:"))
async def show_category(call: CallbackQuery) -> None:
    await call.answer(); category = call.data.split(":", 1)[1]
    await call.message.answer(CATEGORY_NAMES[category], reply_markup=food_list(category))


@router.callback_query(F.data.startswith("food:"), ~F.data.in_({"food:search"}))
async def show_food(call: CallbackQuery) -> None:
    await call.answer(); slug = call.data.split(":", 1)[1]
    text, markup = food_card(slug)
    await call.message.answer(text, reply_markup=markup)


@router.callback_query(F.data.startswith("portion:"))
async def select_portion(call: CallbackQuery) -> None:
    await call.answer(); _, slug, grams = call.data.split(":")
    text, markup = food_card(slug, int(grams))
    await call.message.edit_text(text, reply_markup=markup)


@router.callback_query(F.data.startswith("portion_custom:"))
async def custom_portion(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer(); slug = call.data.split(":", 1)[1]
    await state.set_state(FoodLookup.portion); await state.set_data({"food_slug": slug})
    await call.message.answer(f"Введите массу продукта «{FOODS[slug].name}» в граммах:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu:home")],
    ]))


@router.message(FoodLookup.portion)
async def custom_portion_value(message: Message, state: FSMContext) -> None:
    try:
        grams = float((message.text or "").replace(",", "."))
        if not 1 <= grams <= 3000: raise ValueError
    except ValueError:
        return await message.answer("Введите число от 1 до 3000 граммов.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu:home")],
        ]))
    slug = (await state.get_data())["food_slug"]; await state.clear()
    text, markup = food_card(slug, round(grams))
    await message.answer(text, reply_markup=markup)


@router.callback_query(F.data == "food:search")
async def begin_search(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer(); await state.set_state(FoodLookup.search)
    await call.message.answer("Введите название продукта, например «творог» или «рис»:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu:home")],
    ]))


@router.message(FoodLookup.search)
async def search_food(message: Message, state: FSMContext) -> None:
    query = (message.text or "").strip().lower()
    found = [item for item in FOODS.values() if query in item.name.lower()][:10]
    if not found:
        return await message.answer("Ничего не найдено. Попробуйте более короткое название.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu:home")],
        ]))
    await state.clear()
    markup = InlineKeyboardMarkup(inline_keyboard=[
        *[[InlineKeyboardButton(text=item.name, callback_data=f"food:{item.slug}")] for item in found],
        [InlineKeyboardButton(text="← Каталог", callback_data="menu:foods")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu:home")],
    ])
    await message.answer(f"Найдено: {len(found)}", reply_markup=markup)


def menu_periods() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="На один день", callback_data="mealplan:day")],
        [InlineKeyboardButton(text="На неделю", callback_data="mealplan:week")],
        [InlineKeyboardButton(text="← Меню", callback_data="menu:home")],
    ])


@router.callback_query(F.data == "diet:show")
async def dietary_settings(call: CallbackQuery) -> None:
    await call.answer(); preference = await get_dietary_preferences(call.from_user.id)
    current = preference.raw_text if preference and preference.raw_text else "ограничения не указаны"
    await call.message.answer(
        f"🚫 Пищевые ограничения\nСейчас: {current}\n\nУкажите продукты, которые не едите, не любите или не переносите.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Изменить", callback_data="diet:edit")],
            [InlineKeyboardButton(text="🗑 Очистить", callback_data="diet:clear")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu:home")],
        ]),
    )


@router.callback_query(F.data == "diet:edit")
async def edit_dietary_settings(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer(); await state.set_state(DietarySettings.exclusions)
    await call.message.answer(
        "Напишите одной фразой, например:\n«Не ем рыбу и яблоки, непереносимость лактозы».\n\nПри аллергии всегда проверяйте этикетку и возможные следы аллергенов.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu:home")]]),
    )


@router.message(DietarySettings.exclusions)
async def save_dietary_settings(message: Message, state: FSMContext) -> None:
    raw = (message.text or "").strip()
    if not raw or len(raw) > 500:
        return await message.answer("Опишите ограничения текстом до 500 символов.")
    excluded = parse_exclusions(raw)
    await save_dietary_preferences(message.from_user.id, raw, excluded); await state.clear()
    names = ", ".join(FOODS[slug].name for slug in excluded) or "нет распознанных исключений"
    await message.answer(
        f"✅ Сохранено. FORMETR исключит: {names}.\nЕсли аллергия тяжёлая, автоматически составленное меню требует ручной проверки.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu:home")]]),
    )


@router.callback_query(F.data == "diet:clear")
async def clear_dietary_settings(call: CallbackQuery) -> None:
    await call.answer(); await save_dietary_preferences(call.from_user.id, "", [])
    await call.message.answer("Ограничения очищены.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu:home")]]))


@router.callback_query(F.data == "menu:mealplan")
async def meal_plan_home(call: CallbackQuery) -> None:
    await call.answer()
    await call.message.answer("🍽 Составить примерное меню под вашу калорийность:", reply_markup=menu_periods())


@router.callback_query(F.data.in_({"mealplan:day", "mealplan:week"}))
async def make_meal_plan(call: CallbackQuery) -> None:
    await call.answer(); dashboard = await get_dashboard(call.from_user.id)
    if not dashboard or not dashboard[3]:
        return await call.message.answer("Расчёт меню недоступен без взрослого безопасного ориентира калорийности.", reply_markup=menu_periods())
    calories = dashboard[3].calories
    preference = await get_dietary_preferences(call.from_user.id)
    excluded = set(preference.excluded_foods if preference else [])
    try:
        text = format_week(calories, excluded) if call.data.endswith("week") else format_day(calories, excluded=excluded)
    except ValueError as error:
        return await call.message.answer(f"Не удалось безопасно собрать меню: {error}. Уточните ограничения.", reply_markup=menu_periods())
    if call.data.endswith("week"):
        rows = [[InlineKeyboardButton(text=f"День {day}", callback_data=f"mealplan:week_day:{day}") for day in range(start, min(start + 3, 8))] for start in (1, 4, 7)]
        rows.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu:home")])
    else:
        rows = [[InlineKeyboardButton(text="🔄 Другой вариант дня", callback_data="mealplan:day_alt")], [InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu:home")]]
    await call.message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data == "mealplan:day_alt")
async def alternate_day(call: CallbackQuery) -> None:
    await call.answer(); dashboard = await get_dashboard(call.from_user.id); preference = await get_dietary_preferences(call.from_user.id)
    await call.message.answer(format_day(dashboard[3].calories, 1, set(preference.excluded_foods if preference else [])), reply_markup=menu_periods())


@router.callback_query(F.data.startswith("mealplan:week_day:"))
async def show_week_day(call: CallbackQuery) -> None:
    await call.answer(); day = int(call.data.rsplit(":", 1)[1]); dashboard = await get_dashboard(call.from_user.id)
    preference = await get_dietary_preferences(call.from_user.id)
    text = format_day(dashboard[3].calories, day - 1, set(preference.excluded_foods if preference else []))
    await call.message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="← К выбору периода", callback_data="menu:mealplan")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu:home")],
    ]))
