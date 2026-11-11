"""
Unit-тесты для парсера текстовых сообщений о расходах.
"""

from decimal import Decimal
import pytest
from app.services.parser import parse_expense_text, ParsedExpense, MAX_DESCRIPTION_LENGTH, MAX_EXPENSE_AMOUNT


@pytest.mark.parametrize(
    "text, expected_amount, expected_desc",
    [
        ("кофе 150", Decimal("150.00"), "кофе"),
        ("такси 420.50", Decimal("420.50"), "такси"),
        ("обед 250,75", Decimal("250.75"), "обед"),
        ("150 кофе", Decimal("150.00"), "кофе"),
        ("420.50 такси", Decimal("420.50"), "такси"),
        ("3000 аренда квартиры", Decimal("3000.00"), "аренда квартиры"),
        ("кофе с молоком 250", Decimal("250.00"), "кофе с молоком"),
        ("пицца 2 шт 800", Decimal("800.00"), "пицца 2 шт"),
        ("метро 65 ₽", Decimal("65.00"), "метро"),
        ("булочка 45 руб", Decimal("45.00"), "булочка"),
        ("бензин 1500р", Decimal("1500.00"), "бензин"),
    ]
)
def test_valid_expense_parsing(text: str, expected_amount: Decimal, expected_desc: str):
    """Проверка корректного распознавания различных форматов ввода."""
    result = parse_expense_text(text)
    assert result is not None
    assert result.amount == expected_amount
    assert result.description == expected_desc


@pytest.mark.parametrize(
    "invalid_text",
    [
        "",                     # Пустая строка
        "   ",                  # Только пробелы
        "кофе",                 # Нет суммы
        "просто текст без сумм",
        "150",                  # Только сумма без описания
        "500.50",               # Только сумма с копейками
        "кофе 0",               # Нулевая сумма
        "такси 0.00",           # Нулевая сумма
        "кофе -150",            # Отрицательная сумма
        "такси -420.50",        # Отрицательная дробная сумма
        "кофе 150.999",         # Более 2 знаков после запятой
        f"квартира {MAX_EXPENSE_AMOUNT + 1000}", # Превышение максимального лимита
    ]
)
def test_invalid_expense_parsing(invalid_text: str):
    """Проверка обработки некорректных форматов ввода и граничных значений."""
    result = parse_expense_text(invalid_text)
    assert result is None


def test_long_description_truncation():
    """Проверка обрезки слишком длинного описания до лимита MAX_DESCRIPTION_LENGTH."""
    long_desc = "а" * 300
    text = f"{long_desc} 500"
    result = parse_expense_text(text)
    
    assert result is not None
    assert result.amount == Decimal("500.00")
    assert len(result.description) <= MAX_DESCRIPTION_LENGTH
    assert result.description == "а" * MAX_DESCRIPTION_LENGTH
