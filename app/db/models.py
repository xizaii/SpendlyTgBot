"""
Модели базы данных (SQLAlchemy 2.0).
"""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import BigInteger, DateTime, Numeric, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Базовый класс для всех моделей базы данных."""
    pass


class Expense(Base):
    """
    Модель траты (расхода).
    Каждая запись строго привязана к Telegram user_id.
    Сумма хранится в Decimal (тип Numeric(12, 2)), чтобы избежать ошибок округления float.
    """
    __tablename__ = "expenses"

    # Уникальный идентификатор записи
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Идентификатор пользователя в Telegram (индексирован для быстрого поиска)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)

    # Сумма расхода: до 12 знаков всего, 2 знака после запятой (например: 1234567890.50)
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=12, scale=2), nullable=False)

    # Краткое описание траты (например: "кофе с круассаном")
    description: Mapped[str] = mapped_column(String(255), nullable=False)

    # Категория траты (например: "Еда", "Транспорт", "Прочее")
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="Прочее")

    # Дата и время создания записи (автоматически на стороне БД)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    def __repr__(self) -> str:
        return (
            f"<Expense(id={self.id}, user_id={self.user_id}, "
            f"amount={self.amount}, category='{self.category}', description='{self.description}')>"
        )
