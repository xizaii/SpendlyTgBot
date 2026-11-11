"""
Обработчик добавления трат из текстовых сообщений, а также команд /last и /undo.
"""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from app.db.crud import add_expense, delete_last_expense, get_last_expenses
from app.db.database import async_session_maker
from app.handlers.reports import format_amount
from app.services.categorizer import detect_category
from app.services.parser import parse_expense_text

router = Router(name="expenses")


@router.message(Command("last"))
async def cmd_last(message: Message) -> None:
    """
    Обработчик команды /last.
    Показывает последние 10 трат пользователя.
    """
    if not message.from_user:
        return

    async with async_session_maker() as session:
        expenses = await get_last_expenses(session, user_id=message.from_user.id, limit=10)

    if not expenses:
        await message.answer("У вас пока нет сохранённых расходов.")
        return

    lines = ["<b>🕒 Последние расходы:</b>\n"]
    for idx, exp in enumerate(expenses, 1):
        # Форматируем дату (ДД.ММ в UTC/локальном)
        date_str = exp.created_at.strftime("%d.%m %H:%M")
        lines.append(
            f"{idx}. <b>{exp.description}</b> — {format_amount(exp.amount)} "
            f"<i>({exp.category})</i> [{date_str}]"
        )

    await message.answer("\n".join(lines))


@router.message(Command("undo"))
async def cmd_undo(message: Message) -> None:
    """
    Обработчик команды /undo.
    Удаляет последнюю записанную трату пользователя.
    """
    if not message.from_user:
        return

    async with async_session_maker() as session:
        deleted_expense = await delete_last_expense(session, user_id=message.from_user.id)

    if deleted_expense is None:
        await message.answer("У вас нет расходов для удаления.")
        return

    await message.answer(
        f"🗑 <b>Удалена последняя трата:</b>\n"
        f"• <b>{deleted_expense.description}</b> — {format_amount(deleted_expense.amount)} "
        f"<i>({deleted_expense.category})</i>"
    )


@router.message(F.text)
async def handle_expense_text(message: Message) -> None:
    """
    Обработчик всех текстовых сообщений.
    Пытается распарсить текст как расход (описание + сумма).
    В случае успеха сохраняет в БД и подтверждает запись.
    В случае ошибки выдаёт вежливую подсказку с примерами.
    """
    if not message.text or not message.from_user:
        return

    parsed = parse_expense_text(message.text)
    if not parsed:
        hint_text = (
            "⚠️ <b>Не удалось распознать трату.</b>\n\n"
            "Пожалуйста, отправьте сообщение в формате:\n"
            "<code>описание сумма</code> или <code>сумма описание</code>\n\n"
            "<b>Примеры:</b>\n"
            "• <code>кофе 150</code>\n"
            "• <code>такси 420.50</code>\n"
            "• <code>3000 аренда</code>\n"
            "• <code>продукты 1200,90</code>"
        )
        await message.answer(hint_text)
        return

    # Автоматически определяем категорию по описанию
    category = detect_category(parsed.description)

    # Сохраняем в базу данных
    async with async_session_maker() as session:
        await add_expense(
            session=session,
            user_id=message.from_user.id,
            amount=parsed.amount,
            description=parsed.description,
            category=category
        )

    # Отправляем подтверждение пользователю
    await message.answer(
        f"✅ <b>Записано:</b> {parsed.description} — {format_amount(parsed.amount)} "
        f"<i>({category})</i>"
    )
