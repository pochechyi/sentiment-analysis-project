import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer

# Скачиваем необходимые ресурсы nltk при первом запуске
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')


def analyze_problem_reviews_nltk(df):
    """Анализ отзывов с использованием nltk"""

    # Инициализируем стеммер для русского языка
    stemmer = SnowballStemmer("russian")

    # Стеммы ключевых слов (основы слов)
    problem_keywords_stems = {
        'брак': ['брак'],
        'качество': ['качеств'],
        'отказ': ['отказ'],
        'возврат': ['возврат', 'вернут'],
        'разочарование': ['разочарован'],
        'проблема': ['проблем'],
        'дефект': ['дефект'],
        'недостаток': ['недостаток'],
        'обман': ['обман'],
        'поломка': ['поломк', 'сломан'],
        'обидно': ['обидн'],
        'не решена': ['нерешен', 'не решен'],
        'не понравилось': ['непонрав', 'не понрав'],
        'позорище': ['позор'],
        'ужас': ['ужас'],
        'кошмар': ['кошмар'],
        'отвратительно': ['отвратительн'],
        'гадость': ['гадост'],
        'мусор': ['мусор'],
        'выбросил': ['выброс', 'выкид'],
        'просроченный':['сроч','срок']
    }

    text_col = 'Текст отзыва'
    rating_col = 'Количество звезд'

    if text_col not in df.columns:
        print("Колонка с текстом отзывов не найдена!")
        return

    print("=" * 80)
    print("АНАЛИЗ ОТЗЫВОВ С ИСПОЛЬЗОВАНИЕМ NLTK")
    print("=" * 80)

    # Русские стоп-слова
    russian_stopwords = set(stopwords.words('russian'))

    problem_reviews = []

    for idx, row in df.iterrows():
        review_text = str(row[text_col])
        rating = row[rating_col] if rating_col in df.columns else 'N/A'

        # Токенизация и нормализация текста
        tokens = word_tokenize(review_text.lower(), language='russian')

        # Убираем стоп-слова и знаки препинания
        clean_tokens = [token for token in tokens
                        if token.isalpha() and token not in russian_stopwords]

        # Приводим слова к основам (стемминг)
        stems = [stemmer.stem(token) for token in clean_tokens]

        found_keywords = []

        # Ищем ключевые стеммы в тексте
        for category, keyword_stems in problem_keywords_stems.items():
            for keyword_stem in keyword_stems:
                if keyword_stem in stems:
                    found_keywords.append(category)
                    break

        if found_keywords:
            problem_reviews.append({
                'id': idx,
                'rating': rating,
                'keywords': ', '.join(sorted(set(found_keywords))),
                'text': review_text[:200] + '...' if len(review_text) > 200 else review_text,
                'full_text': review_text,
                'tokens': clean_tokens,  # для отладки
                'stems': stems  # для отладки
            })

    # Выводим результаты
    if problem_reviews:
        print(f"Найдено отзывов с проблемными словами: {len(problem_reviews)}")

        # Статистика
        keyword_stats = {}
        for review in problem_reviews:
            for keyword in review['keywords'].split(', '):
                keyword_stats[keyword] = keyword_stats.get(keyword, 0) + 1

        print("\n📊 СТАТИСТИКА ПО КЛЮЧЕВЫМ СЛОВАМ (NLTK):")
        for keyword, count in sorted(keyword_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  🔸 {keyword}: {count} отзывов")

        # Примеры найденных слов
        print("\n🔍 ПРИМЕРЫ ОБРАБОТКИ ТЕКСТА:")
        print("-" * 50)

        for i, review in enumerate(problem_reviews[:3], 1):
            print(f"Пример {i}:")
            print(f"Оригинал: {review['full_text'][:100]}...")
            print(f"Токены: {review['tokens'][:10]}...")
            print(f"Стеммы: {review['stems'][:10]}...")
            print(f"Найденные категории: {review['keywords']}")
            print("-" * 40)

        # Детальный анализ
        print("\n📝 ДЕТАЛЬНЫЙ АНАЛИЗ ОТЗЫВОВ:")
        print("-" * 80)

        for i, review in enumerate(problem_reviews[:10], 1):
            print(f"{i}. ⭐ {review['rating']} | {review['keywords']}")
            print(f"   Текст: {review['text']}")
            print("-" * 60)

    else:
        print("Отзывов с проблемными словами не найдено.")

    return problem_reviews


def sentiment_analysis_nltk(df):
    """Анализ тональности с использованием nltk"""

    text_col = 'Текст отзыва'

    if text_col not in df.columns:
        return

    print("\n" + "=" * 80)
    print("АНАЛИЗ ТОНАЛЬНОСТИ С NLTK")
    print("=" * 80)

    # Словари для анализа тональности (упрощенный подход)
    positive_words = {'хорош', 'отличн', 'прекрасн', 'доволен', 'рекомендую', 'люблю', 'восхитительн'}
    negative_words = {'плох', 'ужасн', 'разочарован', 'неудобн', 'некачественен', 'ненавижу', 'отвратительн'}

    stemmer = SnowballStemmer("russian")

    sentiment_results = []

    for idx, row in df.iterrows():
        review_text = str(row[text_col])

        # Токенизация и стемминг
        tokens = word_tokenize(review_text.lower(), language='russian')
        clean_tokens = [token for token in tokens if token.isalpha()]
        stems = [stemmer.stem(token) for token in clean_tokens]

        # Подсчет тональности
        positive_score = sum(1 for stem in stems if stem in positive_words)
        negative_score = sum(1 for stem in stems if stem in negative_words)

        if positive_score > negative_score:
            sentiment = 'positive'
        elif negative_score > positive_score:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'

        sentiment_results.append({
            'text': review_text,
            'sentiment': sentiment,
            'positive_score': positive_score,
            'negative_score': negative_score
        })

    # Статистика тональности
    from collections import Counter
    sentiment_counts = Counter([r['sentiment'] for r in sentiment_results])

    print("Распределение тональности:")
    print(f"✅ Положительные: {sentiment_counts['positive']}")
    print(f"⚠️  Нейтральные: {sentiment_counts['neutral']}")
    print(f"❌ Отрицательные: {sentiment_counts['negative']}")

    return sentiment_results