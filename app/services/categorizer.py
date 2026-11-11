"""
Сервис автоматического определения категории расхода по описанию.
"""

import re
from app.services.categories_data import CATEGORIES_KEYWORDS, DEFAULT_CATEGORY


def detect_category(description: str) -> str:
    """
    Определяет категорию расхода на основе анализа ключевых слов в описании.
    
    Алгоритм:
    1. Приводит текст к нижнему регистру.
    2. Очищает от лишней пунктуации, оставляя буквы, цифры и пробелы.
    3. Проверяет наличие ключевых слов/стеммов в тексте.
    4. Если найдено совпадение — возвращает соответствующую категорию.
    5. Если совпадений нет — возвращает категорию по умолчанию ("Прочее").
    """
    if not description:
        return DEFAULT_CATEGORY

    # Приводим к нижнему регистру и нормализуем пробелы
    normalized_text = description.lower()
    
    # Разбиваем текст на отдельные слова для точного и подстрочного поиска
    words = re.findall(r"[а-яa-z0-9ё]+", normalized_text)

    # Проходим по категориям и их ключевым словам
    for category, keywords in CATEGORIES_KEYWORDS.items():
        for keyword in keywords:
            kw = keyword.lower()
            # Проверяем, есть ли ключевое слово как подстрока в любом из слов описания
            # или как часть всего текста целиком (для словосочетаний вроде "яндекс плюс")
            if " " in kw:
                if kw in normalized_text:
                    return category
            else:
                for word in words:
                    if kw in word:
                        return category

    return DEFAULT_CATEGORY
