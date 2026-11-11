"""
Функции CRUD (Create, Read, Update, Delete) для работы с расходами в базе данных.
Все запросы строго изолируют данные по user_id.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Expense


async def add_expense(
    session: AsyncSession,
    user_id: int,
    amount: Decimal,
    description: str,
    category: str
) -> Expense:
    """
    Добавляет новую запись о расходе в базу данных.
    """
    expense = Expense(
        user_id=user_id,
        amount=amount,
        description=description,
        category=category
    )
    session.add(expense)
    await session.commit()
    await session.refresh(expense)
    return expense


async def get_last_expenses(
    session: AsyncSession,
    user_id: int,
    limit: int = 10
) -> List[Expense]:
    """
    Возвращает список последних N расходов конкретного пользователя.
    Сортировка от самых новых к более старым.
    """
    stmt = (
        select(Expense)
        .where(Expense.user_id == user_id)
        .order_by(Expense.created_at.desc(), Expense.id.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def delete_last_expense(
    session: AsyncSession,
    user_id: int
) -> Optional[Expense]:
    """
    Находит и удаляет самый последний добавленный расход пользователя.
    Возвращает удалённый объект расхода (чтобы показать пользователю, что удалено)
    или None, если у пользователя нет записей.
    """
    # Ищем последнюю запись
    stmt = (
        select(Expense)
        .where(Expense.user_id == user_id)
        .order_by(Expense.created_at.desc(), Expense.id.desc())
        .limit(1)
    )
    result = await session.execute(stmt)
    expense = result.scalar_one_or_none()

    if expense is not None:
        await session.delete(expense)
        await session.commit()
        return expense

    return None


async def get_expenses_summary(
    session: AsyncSession,
    user_id: int,
    start_date: datetime
) -> Dict[str, Any]:
    """
    Формирует сводку расходов пользователя с даты `start_date` до текущего момента:
    - Общая сумма расходов.
    - Разбивка по категориям (отсортированная по убыванию суммы).
    """
    # 1. Запрос общей суммы за период
    total_stmt = (
        select(func.coalesce(func.sum(Expense.amount), Decimal("0.00")))
        .where(
            Expense.user_id == user_id,
            Expense.created_at >= start_date
        )
    )
    total_result = await session.execute(total_stmt)
    total_amount: Decimal = total_result.scalar_one()

    # 2. Запрос группировки по категориям
    cat_stmt = (
        select(Expense.category, func.sum(Expense.amount).label("cat_total"))
        .where(
            Expense.user_id == user_id,
            Expense.created_at >= start_date
        )
        .group_by(Expense.category)
        .order_by(func.sum(Expense.amount).desc())
    )
    cat_result = await session.execute(cat_stmt)
    by_category: List[tuple[str, Decimal]] = [
        (row[0], Decimal(row[1])) for row in cat_result.all()
    ]

    return {
        "total": total_amount,
        "by_category": by_category
    }
