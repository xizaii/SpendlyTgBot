"""
Обработчики аналитических команд отчётов: /today, /week, /month.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from app.db.crud import get_expenses_summary
from app.db.database import async_session_maker

router = Router(name="reports")

# Эмодзи для известных категорий
CATEGORY_ICONS = {
    "Еда": "🍔",
    "Транспорт": "🚕",
    "Жильё": "🏠",
    "Развлечения": "🎬",
    "Здоровье": "💊",
    "Прочее": "📦"
}


def format_amount(amount: Decimal) -> str:
    """Форматирует Decimal сумму для красивого отображения в Telegram."""
    if amount == amount.to_integral_value():
        return f"{int(amount):,} ₽".replace(",", " ")
    return f"{amount:,.2f} ₽".replace(",", " ")


def build_summary_text(title: str, summary_data: dict) -> str:
    """
    Формирует и форматирует текст отчёта с общей суммой и разбивкой по категориям.
    """
    total: Decimal = summary_data["total"]
    by_category: list[tuple[str, Decimal]] = summary_data["by_category"]

    if total <= Decimal("0.00") or not by_category:
        return f"📊 <b>{title}</b>\n\nЗа этот период трат пока не было. Отличная экономия! 🎉"

    lines = [
        f"📊 <b>{title}</b>",
        f"Итого потрачено: <b>{format_amount(total)}</b>\n",
        "<b>По категориям:</b>"
    ]

    for category, cat_amount in by_category:
        icon = CATEGORY_ICONS.get(category, "🔹")
        percent = (cat_amount / total) * 100
        lines.append(
            f"{icon} <b>{category}</b>: {format_amount(cat_amount)} ({percent:.1f}%)"
        )

    return "\n".join(lines)


@router.message(Command("today"))
async def cmd_today(message: Message) -> None:
    """
    Обработчик команды /today.
    Показывает расходы с начала сегодняшнего дня (00:00:00).
    """
    if not message.from_user:
        return

    # Начало текущего дня (в UTC)
    now = datetime.now(timezone.utc)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

    async with async_session_maker() as session:
        summary = await get_expenses_summary(
            session=session,
            user_id=message.from_user.id,
            start_date=start_of_day
        )

    text = build_summary_text("Расходы за сегодня", summary)
    await message.answer(text)


@router.message(Command("week"))
async def cmd_week(message: Message) -> None:
    """
    Обработчик команды /week.
    Показывает расходы за последние 7 дней.
    """
    if not message.from_user:
        return

    now = datetime.now(timezone.utc)
    start_of_week = now - timedelta(days=7)

    async with async_session_maker() as session:
        summary = await get_expenses_summary(
            session=session,
            user_id=message.from_user.id,
            start_date=start_of_week
        )

    text = build_summary_text("Расходы за последние 7 дней", summary)
    await message.answer(text)


@router.message(Command("month"))
async def cmd_month(message: Message) -> None:
    """
    Обработчик команды /month.
    Показывает расходы за последние 30 дней.
    """
    if not message.from_user:
        return

    now = datetime.now(timezone.utc)
    start_of_month = now - timedelta(days=30)

    async with async_session_maker() as session:
        summary = await get_expenses_summary(
            session=session,
            user_id=message.from_user.id,
            start_date=start_of_month
        )

    text = build_summary_text("Расходы за последние 30 дней", summary)
    await message.answer(text)
