"""
Скрипт для быстрой проверки тестов без необходимости установки внешних библиотек.
"""

from decimal import Decimal
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.parser import parse_expense_text, MAX_DESCRIPTION_LENGTH, MAX_EXPENSE_AMOUNT
from app.services.categorizer import detect_category


def run_all_tests():
    print("Запуск проверки тестов парсера и категоризатора...")
    passed = 0
    total = 0

    # 1. Тесты парсера (валидные)
    valid_cases = [
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
    for text, expected_amount, expected_desc in valid_cases:
        total += 1
        res = parse_expense_text(text)
        assert res is not None, f"Не удалось распарсить '{text}'"
        assert res.amount == expected_amount, f"Сумма не совпала для '{text}': {res.amount} != {expected_amount}"
        assert res.description == expected_desc, f"Описание не совпало для '{text}': {res.description} != {expected_desc}"
        passed += 1

    # 2. Тесты парсера (невалидные)
    invalid_cases = [
        "", "   ", "кофе", "150", "кофе 0", "кофе -150", "кофе 150.999",
        f"квартира {MAX_EXPENSE_AMOUNT + 1000}"
    ]
    for text in invalid_cases:
        total += 1
        res = parse_expense_text(text)
        assert res is None, f"Ожидался None для '{text}', но получено {res}"
        passed += 1

    # 3. Тест обрезки длинного описания
    total += 1
    long_desc = "а" * 300
    res = parse_expense_text(f"{long_desc} 500")
    assert res is not None
    assert len(res.description) == MAX_DESCRIPTION_LENGTH
    passed += 1

    # 4. Тесты категорий
    category_cases = [
        ("кофе", "Еда"),
        ("Капучино в кофейне", "Еда"),
        ("Обед в столовой", "Еда"),
        ("пицца пепперони", "Еда"),
        ("такси до аэропорта", "Транспорт"),
        ("поездка на метро", "Транспорт"),
        ("бензин на лукойле", "Транспорт"),
        ("аренда квартиры", "Жильё"),
        ("оплата жкх", "Жильё"),
        ("билеты в кино", "Развлечения"),
        ("подписка netflix", "Развлечения"),
        ("покупка в аптеке", "Здоровье"),
        ("прием у врача", "Здоровье"),
        ("купил ноутбук", "Прочее"),
        ("", "Прочее"),
    ]
    for desc, expected_cat in category_cases:
        total += 1
        cat = detect_category(desc)
        assert cat == expected_cat, f"Категория не совпала для '{desc}': {cat} != {expected_cat}"
        passed += 1

    print(f"Все {passed} из {total} тестов успешно пройдены!")


if __name__ == "__main__":
    run_all_tests()
