"""
Управление подключением к базе данных PostgreSQL через asyncpg и SQLAlchemy 2.0.
"""

import logging
from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)
from app.config import settings
from app.db.models import Base

logger = logging.getLogger(__name__)

# Создание асинхронного движка SQLAlchemy
# echo=False отключает избыточный вывод SQL-запросов в консоль
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,  # Проверяет живое ли соединение перед отправкой запроса
)

# Фабрика асинхронных сессий
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False  # Объекты остаются доступными после коммита
)


async def init_db() -> None:
    """
    Автоматическое создание всех необходимых таблиц при старте приложения,
    если они ещё не созданы в базе данных.
    """
    logger.info("Проверка и инициализация таблиц базы данных...")
    async with engine.begin() as conn:
        # run_sync выполняет синхронный метод metadata.create_all в асинхронном контексте
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Таблицы базы данных успешно проверены/созданы.")


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Генератор асинхронной сессии для использования в сервисах или хендлерах.
    Гарантирует корректное закрытие сессии после выполнения работы.
    """
    async with async_session_maker() as session:
        yield session


async def check_db_connection() -> bool:
    """
    Проверяет доступность базы данных выполнением простого запроса SELECT 1.
    Используется в эндпоинте /health.
    """
    try:
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.error(f"Ошибка проверки подключения к БД: {exc}")
        return False
