"""
Модуль конфигурации приложения.
Загружает переменные окружения из файла .env или системных переменных.
"""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Класс настроек проекта.
    Все параметры считываются из переменных окружения или файла .env.
    """

    # Токен Telegram-бота от @BotFather
    BOT_TOKEN: str

    # URL подключения к PostgreSQL
    DATABASE_URL: str

    # Публичный URL приложения (например, https://my-bot.onrender.com)
    # Используется Telegram для отправки обновлений через Webhook
    WEBHOOK_URL: str = ""

    # Секретный токен для заголовка X-Telegram-Bot-Api-Secret-Token
    WEBHOOK_SECRET: str = ""

    # Путь для вебхука на нашем FastAPI сервере
    WEBHOOK_PATH: str = "/webhook"

    # Параметры запуска веб-сервера
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Игнорировать лишние переменные окружения
    )

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str) -> str:
        """
        Автоматически адаптирует URL базы данных для asyncpg:
        Многие сервисы (Render, Neon, Supabase) выдают URL с префиксом postgres:// или postgresql://.
        SQLAlchemy для асинхронного режима требует postgresql+asyncpg://.
        """
        if not isinstance(v, str):
            return v
        
        # Если строка начинается с postgres://, заменяем на postgresql+asyncpg://
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        
        # Если начинается с postgresql:// без указания драйвера, добавляем +asyncpg
        if v.startswith("postgresql://") and not v.startswith("postgresql+asyncpg://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)

        return v

    @property
    def full_webhook_url(self) -> str:
        """Возвращает полный URL вебхука для регистрации в Telegram."""
        base = self.WEBHOOK_URL.rstrip("/")
        return f"{base}{self.WEBHOOK_PATH}"


# Создаём синглтон настроек, который будет импортироваться в других частях программы
settings = Settings()
