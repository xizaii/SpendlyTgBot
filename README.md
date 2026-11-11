# 💰 Telegram-бот для учёта личных расходов (Expense Tracker Bot)

Простой, надёжный и быстрый асинхронный Telegram-бот для персонального учёта расходов.
Работает через **Webhook** на веб-сервере **FastAPI** с базой данных **PostgreSQL** (`SQLAlchemy 2.0` + `asyncpg`).
Готов к бесплатному деплою на облачный хостинг **Render** и облачную БД **Neon** или **Supabase**.

---

## 📌 Возможности бота
1. **Быстрое добавление траты обычным текстом**:
   - `кофе 150` или `150 кофе`
   - `такси 420.50` или `420,50 такси`
   - `3000 аренда квартиры`
2. **Умное автоопределение категории**:
   - Категории: **🍔 Еда**, **🚕 Транспорт**, **🏠 Жильё**, **🎬 Развлечения**, **💊 Здоровье**, **📦 Прочее**.
   - Словарь ключевых слов вынесен в отдельный файл `app/services/categories_data.py` — его легко дополнять.
3. **Отчёты и аналитика**:
   - `/today` — расходы за сегодняшний день (с 00:00).
   - `/week` — расходы за последние 7 дней с разбивкой по категориям и процентами.
   - `/month` — расходы за последние 30 дней.
   - `/last` — список последних 10 трат с датой и временем.
4. **Управление и безопасность**:
   - `/undo` — удаление последней добавленной траты (если опечатались).
   - `/help` — список всех команд и инструкция по вводу.
   - **Строгая изоляция данных**: расходы каждого пользователя привязаны к его `user_id`.
   - **Точные денежные расчёты**: суммы хранятся как `Decimal`/`Numeric(12, 2)`, никаких потерь float.
   - **Защита Webhook**: проверка секретного заголовка `X-Telegram-Bot-Api-Secret-Token`.
   - **Эндпоинт `/health`**: проверка жизнеспособности сервиса и связи с БД.

---

## 📂 Структура проекта

```
expense_tracker_bot/
├── .env.example              # Образец файла переменных окружения
├── .gitignore                # Исключения для Git
├── .dockerignore             # Исключения при сборке Docker
├── Dockerfile                # Сборка контейнера для Render / хостинга
├── requirements.txt          # Зафиксированные версии библиотек
├── pytest.ini                # Конфигурация для запуска тестов
├── README.md                 # Пошаговая инструкция (вы читаете её сейчас)
├── app/
│   ├── __init__.py
│   ├── config.py             # Настройки приложения через pydantic-settings
│   ├── bot.py                # Инициализация Bot и Dispatcher (aiogram 3.x)
│   ├── main.py               # FastAPI веб-сервер, эндпоинты /health и /webhook
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py       # Async engine, sessionmaker, автосоздание таблиц
│   │   ├── models.py         # Модель Expense (SQLAlchemy 2.0)
│   │   └── crud.py           # Запросы к БД: добавление, удаление, выборки
│   ├── services/
│   │   ├── __init__.py
│   │   ├── categories_data.py # Словарь ключевых слов по категориям
│   │   ├── categorizer.py    # Определение категории по тексту
│   │   └── parser.py         # Парсинг сообщений ("кофе 150"), валидация (Decimal)
│   └── handlers/
│       ├── __init__.py
│       ├── common.py         # Команды /start, /help
│       ├── expenses.py       # Обработка текстовых трат, /undo, /last
│       └── reports.py        # Команды /today, /week, /month
└── tests/
    ├── __init__.py
    ├── run_tests.py          # Автономный скрипт для мгновенного прогона тестов
    ├── test_parser.py        # Pytest: тестирование парсера и граничных случаев
    └── test_categorizer.py   # Pytest: тестирование категоризации
```

---

## 🚀 Пошаговая инструкция по деплою (для новичков)

Следуйте этим простым шагам, чтобы бесплатно запустить вашего бота в интернете за 15 минут.

---

### Шаг 1: Создание бота в Telegram через @BotFather

1. Откройте Telegram и найдите официального бота **[@BotFather](https://t.me/BotFather)**.
2. Отправьте команду:
   ```text
   /newbot
   ```
3. Введите название бота (например, `Мой Учёт Расходов`).
4. Введите юзернейм бота, который должен заканчиваться на `bot` (например, `my_budget_tracker_super_bot`).
5. @BotFather поздравит вас и пришлёт **HTTP API Token** (выглядит как `1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ`).
   > ⚠️ **Важно:** Сохраните этот токен и никому не показывайте!
6. (Опционально, но рекомендуется) Настройте подсказки команд в меню бота:
   - Отправьте @BotFather команду `/setcommands`.
   - Выберите своего бота.
   - Отправьте список:
     ```text
     today - Расходы за сегодня
     week - Расходы за последние 7 дней
     month - Расходы за последние 30 дней
     last - Последние 10 трат
     undo - Удалить последнюю трату
     help - Справка и помощь
     ```

---

### Шаг 2: Создание бесплатной базы данных PostgreSQL (Neon.tech)

Мы рекомендуем сервис **[Neon.tech](https://neon.tech/)** — это быстрый бессерверный PostgreSQL с щедрым бесплатным тарифом.

1. Зарегистрируйтесь на сайте [Neon.tech](https://neon.tech/) (можно через GitHub или Google).
2. Нажмите **"Create project"**.
3. Укажите имя проекта (например, `expenses-db`) и нажмите **"Create Project"**.
4. В открывшейся панели управления (Dashboard) найдите блок **Connection Details**.
5. Выберите пункт **Connection string** и скопируйте строку. Она выглядит примерно так:
   ```text
   postgresql://alex:AbCdEf123@ep-cool-flower-123456.eu-central-1.aws.neon.tech/neondb?sslmode=require
   ```
   > 💡 **Примечание:** Наш бот в файле `app/config.py` автоматически преобразует `postgresql://` в `postgresql+asyncpg://`, поэтому можете вставлять строку подключения прямо в таком виде!

*(Альтернатива: можно использовать [Supabase.com](https://supabase.com/), там строка подключения берётся в Project Settings -> Database -> Connection string (URI)).*

---

### Шаг 3: Деплой на бесплатный хостинг Render.com

[Render.com](https://render.com/) позволяет бесплатно запускать веб-сервисы из Docker/GitHub.

#### 3.1. Загрузка кода на GitHub:
1. Создайте бесплатный репозиторий на [GitHub.com](https://github.com) (например, `expense-tracker-bot`).
2. В локальной папке проекта инициализируйте Git и отправьте код в репозиторий:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of expense tracker bot"
   git branch -M main
   git remote add origin https://github.com/ВАШ_ЛОГИН/expense-tracker-bot.git
   git push -u origin main
   ```

#### 3.2. Создание Web Service на Render:
1. Зарегистрируйтесь на [Render.com](https://render.com/) (удобно войти через GitHub).
2. Нажмите синюю кнопку **"New +"** вверху справа и выберите **"Web Service"**.
3. Выберите **"Build and deploy from a Git repository"** и подключите ваш репозиторий `expense-tracker-bot`.
4. Заполните поля формы:
   - **Name**: имя вашего проекта (например, `my-expenses-bot-123`).
   - **Region**: выберите ближайший регион (например, `Frankfurt (EU Central)`).
   - **Language**: выберите **Docker** (Render сам увидит наш `Dockerfile`).
   - **Instance Type**: выберите **Free** ($0 / month).
5. Прокрутите вниз до раздела **Environment Variables** (Переменные окружения) и добавьте 4 переменные:
   - `BOT_TOKEN` — ваш токен от @BotFather (из Шага 1).
   - `DATABASE_URL` — строка подключения к базе от Neon (из Шага 2).
   - `WEBHOOK_URL` — адрес, который Render выделит вашему сервису. Он формируется как `https://ИМЯ_ВАШЕГО_СЕРВИСА.onrender.com` (например, `https://my-expenses-bot-123.onrender.com`).
   - `WEBHOOK_SECRET` — любая случайная секретная строка из букв и цифр (например, `super_secret_token_777_xyz`).
6. Нажмите **"Create Web Service"**.
7. Начнётся сборка Docker-образа. Через 2-3 минуты в логах появится:
   ```text
   Проверка и инициализация таблиц базы данных...
   Таблицы базы данных успешно проверены/созданы.
   Регистрация Webhook в Telegram: https://my-expenses-bot-123.onrender.com/webhook
   Webhook успешно установлен в Telegram.
   Application startup complete.
   ```

---

### Шаг 4: Проверка работы бота

1. **Проверка эндпоинта `/health`**:
   Откройте в браузере:
   `https://ВАШ_СЕРВИС.onrender.com/health`
   Вы должны увидеть ответ:
   ```json
   {"status": "ok", "database": "connected"}
   ```
2. **Проверка статуса Webhook в Telegram**:
   Откройте в браузере ссылку (замените `<ВАШ_ТОКЕН>` на токен бота):
   ```text
   https://api.telegram.org/bot<ВАШ_ТОКЕН>/getWebhookInfo
   ```
   В ответе должно быть `"has_custom_certificate": false`, `"pending_update_count": 0` и ваш URL.
3. **Проверка в Telegram**:
   - Откройте вашего бота в Telegram и отправьте `/start`.
   - Напишите: `кофе 150`.
   - Бот мгновенно ответит: `✅ Записано: кофе — 150 ₽ (Еда)`.
   - Отправьте команду `/today` или `/last` и убедитесь, что трата отображается в отчёте.

---

### Шаг 5: Предотвращение «засыпания» сервиса (UptimeRobot)

На бесплатном тарифе Render Web Service **"засыпает"** (spin down), если на него не поступают HTTP-запросы в течение 15 минут. Первый запрос после засыпания может «будить» бота до 30–50 секунд.

Чтобы бот всегда отвечал мгновенно, настроим бесплатный пинг через [UptimeRobot](https://uptimerobot.com/):

1. Зарегистрируйтесь на сайте [UptimeRobot.com](https://uptimerobot.com/) (бесплатно).
2. Нажмите **"Add New Monitor"**.
3. Заполните параметры:
   - **Monitor Type**: `HTTP(s)`
   - **Friendly Name**: `Expense Bot Health`
   - **URL (or IP)**: `https://ВАШ_СЕРВИС.onrender.com/health`
   - **Monitoring Interval**: каждые `10 minutes` (или 14 minutes).
4. Нажмите **"Create Monitor"**.
5. Теперь UptimeRobot будет регулярно опрашивать лёгкий эндпоинт `/health`, и сервис на Render не уйдёт в спящий режим!

> ⚠️ **Ограничения бесплатного тарифа Render**:
> В бесплатном аккаунте Render даётся **750 бесплатных часов работы инстансов в месяц**.
> Месяц из 31 дня содержит 744 часа. Это значит, что **один сервис может работать круглосуточно 24/7 весь месяц совершенно бесплатно**! Но если создать 2 и более работающих сервиса одновременно, лимит 750 часов закончится раньше конца месяца.

---

## 💻 Локальный запуск и отладка (Local Development)

Если вы хотите тестировать или дорабатывать бота на своём компьютере:

### 1. Подготовка окружения
1. Создайте виртуальное окружение:
   ```bash
   python -m venv venv
   ```
2. Активируйте его:
   - Windows: `venv\Scripts\activate`
   - Linux/macOS: `source venv/bin/activate`
3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
4. Создайте файл `.env`:
   ```bash
   copy .env.example .env     # на Windows
   cp .env.example .env       # на Linux/macOS
   ```
   Укажите в `.env` ваши настоящие `BOT_TOKEN`, `DATABASE_URL` и придумайте `WEBHOOK_SECRET`.

### 2. Настройка туннеля (ngrok или cloudflared)
Так как бот работает через Webhook, Telegram должен отправлять запросы на публичный `https://` адрес. Локальный `localhost:8000` из интернета недоступен.

Используйте бесплатную утилиту **ngrok**:
1. Скачайте и запустите ngrok:
   ```bash
   ngrok http 8000
   ```
2. Ngrok выдаст публичный адрес вида:
   `https://abc1-23-45-67.ngrok-free.app`
3. Укажите этот адрес в переменной `WEBHOOK_URL` в вашем локальном файле `.env`:
   ```env
   WEBHOOK_URL=https://abc1-23-45-67.ngrok-free.app
   ```

### 3. Запуск веб-сервера
Запустите приложение:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Приложение запустится, создаст таблицы в БД, зарегистрирует вебхук через ngrok, и бот начнёт отвечать на сообщения!

---

## 🧪 Запуск тестов

Для проверки корректности работы парсера текста и классификатора категорий:

- **Автономный быстрый запуск (без сторонних пакетов)**:
  ```bash
  python tests/run_tests.py
  ```
- **Запуск через pytest**:
  ```bash
  pytest
  ```

---

## 🛠 Технологический стек
- **Python 3.11+**
- **aiogram 3.x**
- **FastAPI** + **uvicorn**
- **PostgreSQL** + **SQLAlchemy 2.0 (Async)** + **asyncpg**
- **Pydantic Settings**
- **Pytest**
- **Docker**
"# SpendlyTgBot" 
