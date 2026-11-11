"""
Инициализация бота и диспетчера aiogram 3.x.
"""

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app.config import settings

# Инициализируем бота с базовыми настройками (HTML-разметка по умолчанию)
bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

# Главный диспетчер событий aiogram
dp = Dispatcher()


def setup_routers() -> None:
    """
    Регистрирует роутеры хендлеров в диспетчере.
    Порядок регистрации важен: сначала специфичные команды, затем общий текстовый ввод трат.
    """
    from app.handlers.common import router as common_router
    from app.handlers.reports import router as reports_router
    from app.handlers.expenses import router as expenses_router

    dp.include_router(common_router)
    dp.include_router(reports_router)
    dp.include_router(expenses_router)
