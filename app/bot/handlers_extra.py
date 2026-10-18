from aiogram import F
from aiogram.types import CallbackQuery

from app.bot.handlers import router
from app.bot.keyboards import main_menu, review_actions
from app.calculations.trends import calculate_trend, review_progress
from app.database.repositories import get_dashboard, measurement_history, record_review


@router.callback_query(F.data == "menu:progress_review")
async def progress_review(call: CallbackQuery) -> None:
    await call.answer()
    history = await measurement_history(call.from_user.id)
    if not history:
        await call.message.answer("Замеров пока нет.", reply_markup=main_menu())
        return
    lines = [f"📈 История: {len(history)} записей"]
    fields = (("Вес", "weight_kg", "кг"), ("Талия", "waist_cm", "см"), ("Бедро", "thigh_cm", "см"), ("Рука", "arm_cm", "см"), ("Икры", "calf_cm", "см"))
    for label, field, unit in fields:
        values = [getattr(row, field) for row in history if getattr(row, field) is not None]
        trend = calculate_trend(values)
        if trend:
            lines.append(f"{label}: {trend.first_average:g} → {trend.last_average:g} {unit} ({trend.change:+g})")
    dashboard = await get_dashboard(call.from_user.id)
    weights = [row.weight_kg for row in history if row.weight_kg is not None]
    decision, reason, percent = review_progress(weights, dashboard[1].kind)
    lines.append(f"\n{reason}")
    markup = review_actions(percent) if decision == "propose" else main_menu()
    await call.message.answer("\n".join(lines), reply_markup=markup)


@router.callback_query(F.data.startswith("review:"))
async def decide_review(call: CallbackQuery) -> None:
    await call.answer()
    _, action, raw_percent = call.data.split(":")
    accepted = action == "apply"
    new_calories = await record_review(call.from_user.id, accepted, "Корректировка по многонедельному тренду", int(raw_percent))
    if accepted and new_calories:
        text = f"Новая стартовая калорийность: {new_calories} ккал. Белок и жиры сохранены; изменены углеводы."
    elif accepted:
        text = "Автокоррекция питания отключена из-за возрастного или медицинского ограничения."
    else:
        text = "План оставлен без изменений."
    await call.message.answer(text, reply_markup=main_menu())
