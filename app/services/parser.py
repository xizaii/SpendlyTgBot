"""
Сервис парсинга текстовых сообщений с расходами и их валидации.
Поддерживает ввод суммы как в конце ("кофе 150"), так и в начале ("150 кофе").
"""

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Optional

# Максимально допустимая сумма одной траты (10 миллионов рублей)
MAX_EXPENSE_AMOUNT = Decimal("10000000.00")
# Максимальная длина описания (символов)
MAX_DESCRIPTION_LENGTH = 200


@dataclass
class ParsedExpense:
    """Структура успешно распарсенного расхода."""
    amount: Decimal
    description: str


def parse_expense_text(text: str) -> Optional[ParsedExpense]:
    """
    Парсит строку сообщения пользователя и извлекает сумму и описание.
    
    Поддерживаемые форматы:
    - Число в конце: "кофе 150", "такси 420.50", "продукты 1200,90 руб", "метро 60р"
    - Число в начале: "150 кофе", "420.50 такси", "3000 аренда квартиры"
    
    Возвращает ParsedExpense или None, если формат не распознан или не прошёл валидацию.
    """
    if not text:
        return None

    cleaned_text = text.strip()
    # Удаляем возможные знаки валюты в конце строки (руб, р, ₽)
    cleaned_text = re.sub(r"\s*(?:₽|руб\.?|рублей|р\.?)\s*$", "", cleaned_text, flags=re.IGNORECASE).strip()

    # Регулярные выражения:
    # 1. Число в конце строки: "описание 150.50"
    pattern_end = re.compile(r"^(?P<desc>.+?)\s+(?P<amount>\d+(?:[.,]\d{1,2})?)$")
    # 2. Число в начале строки: "150.50 описание"
    pattern_start = re.compile(r"^(?P<amount>\d+(?:[.,]\d{1,2})?)\s+(?P<desc>.+)$")

    match = pattern_end.match(cleaned_text)
    if not match:
        match = pattern_start.match(cleaned_text)

    if not match:
        return None

    raw_amount = match.group("amount").replace(",", ".")
    raw_desc = match.group("desc").strip()

    # Описание не должно быть пустым
    if not raw_desc:
        return None

    # Обрезка слишком длинного текста описания до разумного максимума
    if len(raw_desc) > MAX_DESCRIPTION_LENGTH:
        raw_desc = raw_desc[:MAX_DESCRIPTION_LENGTH].rstrip()

    # Преобразование и валидация суммы
    try:
        amount = Decimal(raw_amount)
    except InvalidOperation:
        return None

    # Округление до 2 знаков после запятой
    amount = round(amount, 2)

    # Валидация: сумма должна быть строго больше нуля и не превышать максимум
    if amount <= Decimal("0.00") or amount > MAX_EXPENSE_AMOUNT:
        return None

    return ParsedExpense(amount=amount, description=raw_desc)
