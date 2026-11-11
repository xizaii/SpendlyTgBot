"""
Точка входа приложения: FastAPI веб-сервер, эндпоинты /health и /webhook,
жизненный цикл (lifespan) с автоматической настройкой базы данных и вебхука.
"""

from contextlib import asynccontextmanager
import logging
import sys
from fastapi import FastAPI, Header, HTTPException, Request, Response, status
from aiogram.types import Update
import uvicorn

from app.bot import bot, dp, setup_routers
from app.config import settings
from app.db.database import check_db_connection, engine, init_db

# Настройка безопасного логирования (без вывода токенов)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("expense_tracker")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения FastAPI:
    - При старте: инициализация БД, регистрация хендлеров, установка Webhook в Telegram.
    - При завершении: закрытие соединений с БД и Telegram API.
    """
    logger.info("Запуск приложения Expense Tracker Bot...")

    # 1. Регистрация роутеров aiogram
    setup_routers()

    # 2. Автоматическое создание таблиц в базе данных
    try:
        await init_db()
    except Exception as e:
        logger.error(f"Не удалось подключиться к базе данных при старте: {e}")

    # 3. Установка Webhook в Telegram
    if settings.WEBHOOK_URL:
        webhook_url = settings.full_webhook_url
        logger.info(f"Регистрация Webhook в Telegram: {webhook_url}")
        try:
            await bot.set_webhook(
                url=webhook_url,
                secret_token=settings.WEBHOOK_SECRET if settings.WEBHOOK_SECRET else None,
                drop_pending_updates=True,
                allowed_updates=["message"]
            )
            logger.info("Webhook успешно установлен в Telegram.")
        except Exception as e:
            logger.error(f"Ошибка при установке Webhook: {e}")
    else:
        logger.warning(
            "WEBHOOK_URL не задан! Бот запущен без автоматической регистрации вебхука."
        )

    yield  # Здесь приложение работает и принимает HTTP-запросы

    # Действия при остановке приложения
    logger.info("Остановка приложения, закрытие ресурсов...")
    try:
        await bot.session.close()
    except Exception as e:
        logger.warning(f"Ошибка при закрытии сессии бота: {e}")

    try:
        await engine.dispose()
    except Exception as e:
        logger.warning(f"Ошибка при закрытии пула соединений БД: {e}")

    logger.info("Приложение остановлено.")


# Создаём приложение FastAPI с жизненным циклом
app = FastAPI(
    title="Expense Tracker Telegram Bot",
    description="Веб-сервер для обработки Webhook Telegram-бота учёта расходов",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health", tags=["Healthcheck"])
async def health_check():
    """
    Эндпоинт проверки жизнеспособности сервиса (healthcheck).
    Используется хостингом Render и внешними пингерами (UptimeRobot).
    Проверяет также статус подключения к базе данных.
    """
    db_ok = await check_db_connection()
    if not db_ok:
        return Response(
            content='{"status": "degraded", "database": "disconnected"}',
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            media_type="application/json"
        )
    return {"status": "ok", "database": "connected"}


@app.post(settings.WEBHOOK_PATH, tags=["Webhook"])
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(None, alias="X-Telegram-Bot-Api-Secret-Token")
):
    """
    Эндпоинт для приёма входящих обновлений от Telegram через Webhook.
    Защищён проверкой секретного токена X-Telegram-Bot-Api-Secret-Token.
    """
    # Проверка секретного токена вебхука
    if settings.WEBHOOK_SECRET:
        if x_telegram_bot_api_secret_token != settings.WEBHOOK_SECRET:
            logger.warning("Попытка отправки запроса на Webhook с неверным секретным токеном!")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Доступ запрещён: неверный секретный токен."
            )

    try:
        data = await request.json()
        update = Update.model_validate(data, context={"bot": bot})
        # Передаём обновление в диспетчер aiogram
        await dp.feed_webhook_update(bot=bot, update=update)
    except Exception as e:
        logger.error(f"Ошибка при обработке обновления Webhook: {e}")
        # Возвращаем 200 OK даже при ошибке обработки, чтобы Telegram не повторял сбойный запрос бесконечно
        return {"ok": False, "error": str(e)}

    return {"ok": True}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False
    )
