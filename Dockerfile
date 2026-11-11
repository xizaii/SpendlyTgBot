# Используем официальный легковесный образ Python 3.11
FROM python:3.11-slim

# Задаём рабочую директорию внутри контейнера
WORKDIR /app

# Отключаем буферизацию вывода Python и создание .pyc файлов
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости без сохранения кэша для уменьшения размера образа
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь исходный код проекта
COPY . .

# Открываем порт по умолчанию (8000)
EXPOSE 8000

# Запуск приложения через uvicorn.
# На Render переменная PORT передаётся автоматически (обычно 10000).
# Конструкция ${PORT:-8000} берёт PORT из окружения, а если она не задана — использует 8000.
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
