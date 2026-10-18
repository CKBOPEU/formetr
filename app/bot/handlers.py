from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.bot.keyboards import choices, main_menu, plan_actions, review_actions
from app.bot.states import GoalChange, MeasurementEntry, Survey
from app.bot.texts import AREA_NAMES, GOAL_NAMES, format_plan
from app.calculations.nutrition import calculate_targets
from app.calculations.safety import needs_medical_review
from app.calculations.trends import calculate_trend, review_progress
from app.database.repositories import (add_measurement, change_goal, change_plan_data, get_dashboard, get_user,
    measurement_history, record_review, reset_user, save_onboarding)
from app.exercises.catalog import CATALOG
from app.services.plans import generate_plan, replace_exercise

router = Router()
SEX = [("Мужской", "male"), ("Женский", "female")]
EXPERIENCE = [("Новичок", "beginner"), ("Средний", "intermediate"), ("Опытный", "advanced")]
ACTIVITY = [("До 5 000 шагов", "low"), ("5–8 тыс.", "light"), ("8–12 тыс.", "moderate"), ("12 тыс.+", "high")]
EQUIPMENT = [("Зал", "gym"), ("Дом", "home"), ("Минимальное оборудование", "minimal")]
GOALS = [("Снизить жировую массу", "fat_loss"), ("Поддерживать форму", "maintain"), ("Набрать мышцы", "muscle_gain"), ("Улучшить композицию", "recomposition"), ("Уменьшить выбранный обхват", "reduce_area")]
AREAS = [("Руки", "arms"), ("Плечи", "shoulders"), ("Бедро/квадрицепс", "thigh"), ("Ягодицы", "glutes"), ("Икры", "calves"), ("Другое", "other")]
MEASUREMENT_FIELDS = {
    "weight_kg": ("Вес", "кг", 30, 300),
    "waist_cm": ("Талия", "см", 20, 250),
    "hips_cm": ("Бёдра", "см", 20, 250),
    "chest_cm": ("Грудь", "см", 20, 250),
    "arm_cm": ("Рука", "см", 10, 100),
    "thigh_cm": ("Бедро", "см", 15, 150),
    "calf_cm": ("Икра", "см", 10, 100),
}


async def _start_survey(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(Survey.name)
    await message.answer("Привет! Я FORMETR — планировщик питания и прогресса. Анкета займёт около двух минут.\n\nКак вас называть?")


@router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    user = await get_user(message.from_user.id)
    if user:
        await message.answer(f"С возвращением, {user.profile.name}!", reply_markup=main_menu())
    else:
        await _start_survey(message, state)


@router.message(Command("reset"))
async def reset(message: Message, state: FSMContext) -> None:
    await reset_user(message.from_user.id)
    await message.answer("Данные тестового профиля удалены. Начинаем заново.")
    await _start_survey(message, state)


@router.message(Command("id"))
async def show_telegram_id(message: Message) -> None:
    await message.answer(f"Ваш Telegram ID: `{message.from_user.id}`", parse_mode="Markdown")


@router.message(Survey.name)
async def survey_name(message: Message, state: FSMContext) -> None:
    if not message.text or not 1 <= len(message.text.strip()) <= 80:
        return await message.answer("Введите имя или ник длиной до 80 символов.")
    await state.update_data(name=message.text.strip())
    await state.set_state(Survey.age)
    await message.answer("Возраст полных лет:")


@router.message(Survey.age)
async def survey_age(message: Message, state: FSMContext) -> None:
    try: value = int(message.text or "")
    except ValueError: return await message.answer("Введите возраст целым числом.")
    if not 12 <= value <= 100: return await message.answer("Допустимый диапазон: 12–100 лет.")
    await state.update_data(age=value); await state.set_state(Survey.sex)
    await message.answer("Пол для расчётной формулы:", reply_markup=choices(SEX, "sex"))


@router.callback_query(Survey.sex, F.data.startswith("sex:"))
async def survey_sex(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer(); await state.update_data(sex=call.data.split(":")[1]); await state.set_state(Survey.height)
    await call.message.answer("Рост в сантиметрах:")


@router.message(Survey.height)
async def survey_height(message: Message, state: FSMContext) -> None:
    try: value = float((message.text or "").replace(",", "."))
    except ValueError: return await message.answer("Введите рост числом, например 170.")
    if not 120 <= value <= 230: return await message.answer("Допустимый диапазон: 120–230 см.")
    await state.update_data(height_cm=value); await state.set_state(Survey.weight)
    await message.answer("Текущий вес в кг:")


@router.message(Survey.weight)
async def survey_weight(message: Message, state: FSMContext) -> None:
    try: value = float((message.text or "").replace(",", "."))
    except ValueError: return await message.answer("Введите вес числом, например 67.5.")
    if not 30 <= value <= 300: return await message.answer("Допустимый диапазон: 30–300 кг.")
    await state.update_data(weight_kg=value); await state.set_state(Survey.activity)
    await message.answer("Средняя бытовая активность:", reply_markup=choices(ACTIVITY, "activity"))


@router.callback_query(Survey.experience, F.data.startswith("experience:"))
async def survey_experience(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer(); await state.update_data(experience=call.data.split(":")[1]); await state.set_state(Survey.activity)
    await call.message.answer("Средняя бытовая активность:", reply_markup=choices(ACTIVITY, "activity"))


@router.callback_query(Survey.activity, F.data.startswith("activity:"))
async def survey_activity(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer()
    await state.update_data(activity=call.data.split(":")[1], experience="beginner", training_days=2, equipment="home", limitations=None)
    await state.set_state(Survey.medical)
    await call.message.answer("Есть беременность, РПП, заболевание или иная ситуация, требующая индивидуального медицинского подхода? Напишите кратко или «нет».")


@router.callback_query(Survey.days, F.data.startswith("days:"))
async def survey_days(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer(); await state.update_data(training_days=int(call.data.split(":")[1])); await state.set_state(Survey.equipment)
    await call.message.answer("Доступное оборудование:", reply_markup=choices(EQUIPMENT, "equipment"))


@router.callback_query(Survey.equipment, F.data.startswith("equipment:"))
async def survey_equipment(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer(); await state.update_data(equipment=call.data.split(":")[1]); await state.set_state(Survey.limitations)
    await call.message.answer("Есть упражнения или движения, которые вы не можете выполнять? Напишите их или «нет».")


@router.message(Survey.limitations)
async def survey_limitations(message: Message, state: FSMContext) -> None:
    value = (message.text or "").strip()
    await state.update_data(limitations=None if value.lower() == "нет" else value)
    await state.set_state(Survey.medical)
    await message.answer("Есть беременность, РПП, заболевание или иная ситуация, требующая индивидуального медицинского подхода? Напишите кратко или «нет».")


@router.message(Survey.medical)
async def survey_medical(message: Message, state: FSMContext) -> None:
    value = (message.text or "").strip()
    await state.update_data(medical_flags=None if value.lower() == "нет" else value)
    await state.set_state(Survey.goal)
    await message.answer("Выберите цель:", reply_markup=choices(GOALS, "goal"))


@router.callback_query(Survey.goal, F.data.startswith("goal:"))
async def survey_goal(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer(); goal = call.data.split(":")[1]; await state.update_data(goal=goal)
    if goal == "reduce_area":
        await state.set_state(Survey.target_area)
        await call.message.answer("Важно: локальное жиросжигание невозможно. Можно влиять на общий уровень жира и тренировочный стимул мышц, но нельзя выбрать место расходования жира.\n\nКакой обхват важен?", reply_markup=choices(AREAS, "area"))
    else:
        await _ask_measurements(call.message, state)


@router.callback_query(Survey.target_area, F.data.startswith("area:"))
async def survey_area(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer(); await state.update_data(target_area=call.data.split(":")[1]); await _ask_measurements(call.message, state)


async def _ask_measurements(message: Message, state: FSMContext) -> None:
    await state.set_state(Survey.measurements)
    await message.answer(
        "Добавьте стартовые замеры по одному. Это необязательно; вес уже сохранён.",
        reply_markup=await _initial_measurement_keyboard(state),
    )


async def _initial_measurement_keyboard(state: FSMContext) -> InlineKeyboardMarkup:
    data = await state.get_data()
    rows = []
    for field, (label, unit, _, _) in MEASUREMENT_FIELDS.items():
        if field == "weight_kg":
            continue
        value = data.get(field)
        text = f"✅ {label}: {value:g} {unit}" if value is not None else f"➕ {label}"
        rows.append([InlineKeyboardButton(text=text, callback_data=f"initial_measure:{field}")])
    rows.append([InlineKeyboardButton(text="Готово — продолжить", callback_data="initial_measure:done")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.callback_query(Survey.measurements, F.data.startswith("initial_measure:"))
async def choose_initial_measurement(call: CallbackQuery, state: FSMContext) -> None:
    field = call.data.split(":", 1)[1]
    if field == "done":
        await call.answer()
        return await _finish_onboarding(call.message, call.from_user.id, call.from_user.username, state)
    await call.answer(); await state.update_data(initial_measurement_field=field)
    await state.set_state(Survey.measurement_value)
    label, unit, _, _ = MEASUREMENT_FIELDS[field]
    await call.message.answer(f"Введите замер «{label}» в {unit}:")


@router.message(Survey.measurement_value)
async def save_initial_measurement(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    field = data["initial_measurement_field"]
    label, unit, minimum, maximum = MEASUREMENT_FIELDS[field]
    try:
        value = float((message.text or "").replace(",", "."))
        if not minimum <= value <= maximum: raise ValueError
    except ValueError:
        return await message.answer(f"Введите значение от {minimum} до {maximum} {unit}.")
    await state.update_data(**{field: value})
    await state.set_state(Survey.measurements)
    await message.answer(f"✅ {label}: {value:g} {unit}", reply_markup=await _initial_measurement_keyboard(state))


async def _finish_onboarding(message: Message, telegram_id: int, username: str | None, state: FSMContext) -> None:
    data = await state.get_data()
    target_fields = {"arms": "arm_cm", "thigh": "thigh_cm", "glutes": "hips_cm", "calves": "calf_cm"}
    target_field = target_fields.get(data.get("target_area"))
    if data["goal"] == "reduce_area" and ("waist_cm" not in data or (target_field and target_field not in data)):
        await state.set_state(Survey.measurements)
        return await message.answer("Для этой цели добавьте отдельно талию и выбранный целевой обхват.", reply_markup=await _initial_measurement_keyboard(state))
    medical = needs_medical_review(data.get("medical_flags"))
    minor = data["age"] < 18
    safe_goal = data["goal"]
    if (minor or medical) and safe_goal in {"fat_loss", "reduce_area"}:
        safe_goal = "maintain"
    nutrition = None if minor or medical else calculate_targets(sex=data["sex"], age=data["age"], height_cm=data["height_cm"], weight_kg=data["weight_kg"], activity=data["activity"], goal=data["goal"])
    plan = generate_plan(data["training_days"], data["experience"], data["equipment"], safe_goal, data.get("target_area"), data.get("limitations"))
    await save_onboarding(telegram_id, username, data, nutrition, plan)
    await state.clear()
    dashboard = await get_dashboard(telegram_id)
    user, goal, stored_plan, stored_nutrition = dashboard
    if stored_nutrition:
        await message.answer(
            f"✅ Ориентир рассчитан: {stored_nutrition.calories} ккал\n"
            f"Белок {stored_nutrition.protein_min}–{stored_nutrition.protein_max} г · "
            f"жиры {stored_nutrition.fat_min}–{stored_nutrition.fat_max} г · "
            f"углеводы около {stored_nutrition.carbs} г.\n\nЭто отправная точка, а не медицинское назначение.",
            reply_markup=main_menu(),
        )
    else:
        await message.answer("Профиль сохранён. Автоматический план питания отключён из-за возрастного или медицинского ограничения.", reply_markup=main_menu())


@router.callback_query(F.data == "menu:home")
async def menu_home(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer(); await state.clear()
    await call.message.answer("Главное меню", reply_markup=main_menu())


@router.callback_query(F.data.in_({"menu:nutrition", "menu:goal"}))
async def show_summary(call: CallbackQuery) -> None:
    await call.answer(); dashboard = await get_dashboard(call.from_user.id)
    if not dashboard: return await call.message.answer("Сначала пройдите /start")
    user, goal, plan, nutrition = dashboard
    if call.data.endswith("nutrition"):
        text = "Автоматический расчёт питания отключён из-за возрастного/медицинского ограничения." if not nutrition else f"🥗 {nutrition.calories} ккал\nБелок {nutrition.protein_min}–{nutrition.protein_max} г\nЖиры {nutrition.fat_min}–{nutrition.fat_max} г\nУглеводы около {nutrition.carbs} г\nКлетчатка {nutrition.fiber}+ г\n\nЭто отправная точка, не медицинское назначение."
    else:
        text = f"🎯 {GOAL_NAMES.get(goal.kind)}" + (f": {AREA_NAMES.get(goal.target_area)}" if goal.target_area else "")
    await call.message.answer(text, reply_markup=main_menu())


@router.callback_query(F.data == "menu:workout")
async def show_workouts(call: CallbackQuery) -> None:
    await call.answer(); dashboard = await get_dashboard(call.from_user.id)
    if not dashboard: return await call.message.answer("Сначала пройдите /start")
    _, goal, plan, nutrition = dashboard
    await call.message.answer(format_plan(goal, nutrition, plan.plan_data), reply_markup=plan_actions(plan.plan_data))


@router.callback_query(F.data.startswith("replace:"))
async def replace(call: CallbackQuery) -> None:
    await call.answer(); _, day, slug = call.data.split(":")
    dashboard = await get_dashboard(call.from_user.id)
    if not dashboard: return
    user, goal, plan, nutrition = dashboard
    updated = replace_exercise(plan.plan_data, int(day), slug, user.profile.equipment)
    await change_plan_data(plan.id, updated)
    await call.message.edit_text(
        format_plan(goal, nutrition, updated),
        reply_markup=plan_actions(updated),
    )


@router.callback_query(F.data == "menu:measurements")
async def measurements_menu(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer(); await state.clear()
    rows = [[InlineKeyboardButton(text=f"{label} ({unit})", callback_data=f"measure:{field}")] for field, (label, unit, _, _) in MEASUREMENT_FIELDS.items()]
    rows.append([InlineKeyboardButton(text="← Меню", callback_data="menu:home")])
    await call.message.answer("Что хотите записать? Каждый показатель сохраняется отдельно.", reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.startswith("measure:"))
async def choose_measurement(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer(); field = call.data.split(":", 1)[1]
    await state.set_state(MeasurementEntry.value); await state.set_data({"measurement_field": field})
    label, unit, _, _ = MEASUREMENT_FIELDS[field]
    await call.message.answer(f"Введите «{label}» в {unit}:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu:home")],
    ]))


@router.message(MeasurementEntry.value)
async def record_measurement(message: Message, state: FSMContext) -> None:
    field = (await state.get_data())["measurement_field"]
    label, unit, minimum, maximum = MEASUREMENT_FIELDS[field]
    try:
        value = float((message.text or "").replace(",", "."))
        if not minimum <= value <= maximum: raise ValueError
    except ValueError:
        return await message.answer(f"Введите значение от {minimum} до {maximum} {unit}.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu:home")],
        ]))
    await add_measurement(message.from_user.id, {field: value}); await state.clear()
    await message.answer(f"✅ {label}: {value:g} {unit}. Замер сохранён.", reply_markup=main_menu())


@router.callback_query(F.data == "menu:progress")
async def progress(call: CallbackQuery) -> None:
    await call.answer(); history = await measurement_history(call.from_user.id)
    if not history: return await call.message.answer("Замеров пока нет.")
    lines = [f"📈 История: {len(history)} записей"]
    fields = (("Вес", "weight_kg", "кг"), ("Талия", "waist_cm", "см"), ("Бедро", "thigh_cm", "см"), ("Рука", "arm_cm", "см"), ("Икры", "calf_cm", "см"))
    for label, field, unit in fields:
        values = [getattr(x, field) for x in history if getattr(x, field) is not None]
        trend = calculate_trend(values)
        if trend: lines.append(f"{label}: {trend.first_average:g} → {trend.last_average:g} {unit} ({trend.change:+g})")
    dashboard = await get_dashboard(call.from_user.id); goal = dashboard[1]
    weights = [x.weight_kg for x in history if x.weight_kg is not None]
    decision, reason, _ = review_progress(weights, goal.kind)
    lines.append(f"\n{reason}")
    await call.message.answer("\n".join(lines), reply_markup=main_menu())


@router.callback_query(F.data == "menu:settings")
async def settings(call: CallbackQuery) -> None:
    await call.answer(); await call.message.answer(
        f"Ваш Telegram ID: `{call.from_user.id}`\n\nДля полного сброса используйте /reset. Цель можно изменить без удаления истории.",
        reply_markup=main_menu(), parse_mode="Markdown",
    )


@router.callback_query(F.data == "goal:change")
async def begin_goal_change(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer()
    await state.set_state(GoalChange.kind)
    await call.message.answer("Выберите новую цель. Прошлая цель и вся история сохранятся.", reply_markup=choices(GOALS, "goal_change"))


@router.callback_query(GoalChange.kind, F.data.startswith("goal_change:"))
async def choose_new_goal(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer()
    kind = call.data.split(":")[1]
    await state.update_data(kind=kind)
    if kind == "reduce_area":
        await state.set_state(GoalChange.target_area)
        await call.message.answer("Локальное жиросжигание невозможно. Выберите обхват:", reply_markup=choices(AREAS, "goal_area"))
    else:
        await _finish_goal_change(call.message, call.from_user.id, state, kind, None)


@router.callback_query(GoalChange.target_area, F.data.startswith("goal_area:"))
async def choose_new_area(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer()
    data = await state.get_data()
    await _finish_goal_change(call.message, call.from_user.id, state, data["kind"], call.data.split(":")[1])


async def _finish_goal_change(message: Message, telegram_id: int, state: FSMContext, kind: str, target_area: str | None) -> None:
    dashboard = await get_dashboard(telegram_id)
    profile = dashboard[0].profile
    medical = needs_medical_review(profile.medical_flags)
    minor = profile.age < 18
    safe_goal = "maintain" if (minor or medical) and kind in {"fat_loss", "reduce_area"} else kind
    nutrition = None if minor or medical else calculate_targets(sex=profile.sex, age=profile.age, height_cm=profile.height_cm, weight_kg=profile.weight_kg, activity=profile.activity, goal=kind)
    plan = generate_plan(profile.training_days, profile.experience, profile.equipment, safe_goal, target_area, profile.limitations)
    await change_goal(telegram_id, kind, target_area, nutrition, plan)
    await state.clear()
    refreshed = await get_dashboard(telegram_id)
    await message.answer(format_plan(refreshed[1], refreshed[3], refreshed[2].plan_data, minor, medical), reply_markup=plan_actions(refreshed[2].plan_data))
