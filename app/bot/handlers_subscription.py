from aiogram import F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice, Message, PreCheckoutQuery

from app.bot.handlers import router
from app.bot.access import subscribe_keyboard
from app.config import get_settings
from app.services.subscriptions import access_status, activate_subscription

SUBSCRIPTION_PERIOD = 30 * 24 * 60 * 60
PAYLOAD = "formetr_pro_monthly_v1"


def terms_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Принимаю условия и перейти к оплате", callback_data="subscription:terms_accept")],
        [InlineKeyboardButton(text="Отмена", callback_data="menu:home")],
    ])


async def send_terms(message: Message) -> None:
    settings = get_settings()
    await message.answer(
        f"FORMETR Pro: {settings.subscription_price_stars} Stars каждые 30 дней с автопродлением.\n\n"
        "Подписка открывает расчёты, планы, дневник, замеры и анализ прогресса. "
        "Это фитнес-планировщик, а не медицинская услуга. Оплата проводится в Telegram Stars. "
        f"Вопросы по оплате: {settings.support_contact}.\n\n"
        "Нажимая кнопку ниже, вы соглашаетесь с этими условиями.",
        reply_markup=terms_keyboard(),
    )


@router.message(Command("subscribe"))
async def subscribe_command(message: Message) -> None:
    await send_terms(message)


@router.callback_query(F.data == "subscription:buy")
async def subscription_buy(call: CallbackQuery) -> None:
    await call.answer()
    await send_terms(call.message)


@router.callback_query(F.data == "subscription:terms_accept")
async def subscription_invoice(call: CallbackQuery) -> None:
    await call.answer()
    settings = get_settings()
    invoice_url = await call.bot.create_invoice_link(
        title="FORMETR Pro",
        description="Полный доступ к фитнес-планировщику на 30 дней. Автопродление.",
        payload=PAYLOAD,
        currency="XTR",
        prices=[LabeledPrice(label="FORMETR Pro / 30 дней", amount=settings.subscription_price_stars)],
        provider_token="",
        subscription_period=SUBSCRIPTION_PERIOD,
    )
    await call.message.answer("Нажмите кнопку, чтобы открыть защищённую форму Telegram Stars.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Оплатить {settings.subscription_price_stars} ⭐", url=invoice_url)],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu:home")],
    ]))


@router.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery) -> None:
    if query.invoice_payload != PAYLOAD:
        await query.answer(ok=False, error_message="Неверный тип подписки.")
        return
    await query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message) -> None:
    payment = message.successful_payment
    if payment.invoice_payload != PAYLOAD:
        return
    expiration = getattr(payment, "subscription_expiration_date", None)
    period_end = await activate_subscription(
        message.from_user.id,
        payment.telegram_payment_charge_id,
        expiration,
        bool(getattr(payment, "is_recurring", True)),
    )
    await message.answer(f"✅ FORMETR Pro активирован до {period_end:%d.%m.%Y}.")


@router.callback_query(F.data == "subscription:status")
async def subscription_status(call: CallbackQuery) -> None:
    await call.answer()
    status = await access_status(call.from_user.id)
    if status.kind == "trial":
        text = f"Пробный период: осталось {status.days_left} дн."
    elif status.kind == "paid":
        text = f"FORMETR Pro активен до {status.expires_at:%d.%m.%Y}."
    elif status.kind == "admin":
        text = "Доступ владельца FORMETR активен без ограничений."
    elif status.kind == "free":
        text = "Вам выдан бессрочный бесплатный доступ к FORMETR."
    else:
        text = "Пробный период завершён."
    markup = None if status.kind in {"admin", "free"} else subscribe_keyboard()
    await call.message.answer(text, reply_markup=markup)


@router.message(Command("terms"))
async def terms(message: Message) -> None:
    await send_terms(message)


@router.message(Command("support", "paysupport"))
async def support(message: Message) -> None:
    await message.answer(f"Поддержка FORMETR: {get_settings().support_contact}. Telegram не обрабатывает вопросы по покупкам внутри этого бота.")
