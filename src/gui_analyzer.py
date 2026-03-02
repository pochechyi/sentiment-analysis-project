import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import tkinter as tk
from tkinter import scrolledtext, ttk
import threading

# Скачиваем необходимые ресурсы nltk
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')


class NLTAnalyzerGUI:
    def __init__(self, df):
        self.df = df
        self.setup_gui()

    def setup_gui(self):
        """Создаем графическое окно"""
        self.root = tk.Tk()
        self.root.title("NLTK Анализ отзывов")
        self.root.geometry("1000x700")

        # Создаем notebook (вкладки)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Вкладка 1: Проблемные отзывы
        self.tab1 = ttk.Frame(notebook)
        notebook.add(self.tab1, text="Проблемные отзывы")

        # Вкладка 2: Тональность
        self.tab2 = ttk.Frame(notebook)
        notebook.add(self.tab2, text="Анализ тональности")

        self.setup_problem_tab()
        self.setup_sentiment_tab()

        # Запускаем анализ автоматически
        self.start_analysis()

    def setup_problem_tab(self):
        """Настраиваем вкладку проблемных отзывов"""
        # Статистика
        stats_frame = ttk.LabelFrame(self.tab1, text="Статистика", padding=10)
        stats_frame.pack(fill='x', padx=5, pady=5)

        self.stats_text = scrolledtext.ScrolledText(stats_frame, height=8, width=100)
        self.stats_text.pack(fill='both', expand=True)

        # Детали отзывов
        details_frame = ttk.LabelFrame(self.tab1, text="Детальный анализ", padding=10)
        details_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.details_text = scrolledtext.ScrolledText(details_frame, height=15, width=100)
        self.details_text.pack(fill='both', expand=True)

    def setup_sentiment_tab(self):
        """Настраиваем вкладку тональности"""
        sentiment_frame = ttk.LabelFrame(self.tab2, text="Анализ тональности", padding=10)
        sentiment_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.sentiment_text = scrolledtext.ScrolledText(sentiment_frame, height=25, width=100)
        self.sentiment_text.pack(fill='both', expand=True)

    def start_analysis(self):
        """Запускаем анализ в отдельном потоке"""
        thread = threading.Thread(target=self.run_analysis)
        thread.daemon = True
        thread.start()

    def run_analysis(self):
        """Выполняем анализ и обновляем GUI"""
        # Анализ проблемных отзывов
        problem_reviews = self.analyze_problem_reviews_nltk()

        # Анализ тональности
        sentiment_results = self.sentiment_analysis_nltk()

        # Обновляем GUI в основном потоке
        self.root.after(0, self.update_gui, problem_reviews, sentiment_results)

    def analyze_problem_reviews_nltk(self):
        """Анализ проблемных отзывов"""
        stemmer = SnowballStemmer("russian")

        problem_keywords_stems = {
            'брак': ['брак'], 'качество': ['качеств'], 'отказ': ['отказ'],
            'возврат': ['возврат', 'вернут'], 'разочарование': ['разочарован'],
            'проблема': ['проблем'], 'дефект': ['дефект'], 'недостаток': ['недостаток'],
            'обман': ['обман'], 'поломка': ['поломк', 'сломан'], 'обидно': ['обидн'],
            'не решена': ['нерешен', 'не решен'], 'не понравилось': ['непонрав', 'не понрав'],
            'позорище': ['позор'], 'ужас': ['ужас'], 'кошмар': ['кошмар'],
            'отвратительно': ['отвратительн'], 'гадость': ['гадост'], 'мусор': ['мусор'],
            'выбросил': ['выброс', 'выкид'], 'просроченный': ['сроч', 'срок']
        }

        text_col = 'Текст отзыва'
        rating_col = 'Количество звезд'

        if text_col not in self.df.columns:
            return []

        russian_stopwords = set(stopwords.words('russian'))
        problem_reviews = []

        for idx, row in self.df.iterrows():
            review_text = str(row[text_col])
            rating = row[rating_col] if rating_col in self.df.columns else 'N/A'

            tokens = word_tokenize(review_text.lower(), language='russian')
            clean_tokens = [token for token in tokens
                            if token.isalpha() and token not in russian_stopwords]
            stems = [stemmer.stem(token) for token in clean_tokens]

            found_keywords = []
            for category, keyword_stems in problem_keywords_stems.items():
                for keyword_stem in keyword_stems:
                    if keyword_stem in stems:
                        found_keywords.append(category)
                        break

            if found_keywords:
                problem_reviews.append({
                    'id': idx, 'rating': rating, 'keywords': ', '.join(sorted(set(found_keywords))),
                    'text': review_text[:200] + '...' if len(review_text) > 200 else review_text,
                    'full_text': review_text
                })

        return problem_reviews

    def sentiment_analysis_nltk(self):
        """Анализ тональности"""
        text_col = 'Текст отзыва'

        if text_col not in self.df.columns:
            return []

        positive_words = {'хорош', 'отличн', 'прекрасн', 'доволен', 'рекомендую', 'люблю', 'восхитительн'}
        negative_words = {'плох', 'ужасн', 'разочарован', 'неудобн', 'некачественен', 'ненавижу', 'отвратительн'}

        stemmer = SnowballStemmer("russian")
        sentiment_results = []

        for idx, row in self.df.iterrows():
            review_text = str(row[text_col])

            tokens = word_tokenize(review_text.lower(), language='russian')
            clean_tokens = [token for token in tokens if token.isalpha()]
            stems = [stemmer.stem(token) for token in clean_tokens]

            positive_score = sum(1 for stem in stems if stem in positive_words)
            negative_score = sum(1 for stem in stems if stem in negative_words)

            if positive_score > negative_score:
                sentiment = 'positive'
            elif negative_score > positive_score:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'

            sentiment_results.append({
                'sentiment': sentiment,
                'positive_score': positive_score,
                'negative_score': negative_score
            })

        return sentiment_results

    def update_gui(self, problem_reviews, sentiment_results):
        """Обновляем графический интерфейс"""
        # Обновляем вкладку проблемных отзывов
        self.update_problem_tab(problem_reviews)

        # Обновляем вкладку тональности
        self.update_sentiment_tab(sentiment_results)

    def update_problem_tab(self, problem_reviews):
        """Обновляем вкладку проблемных отзывов"""
        self.stats_text.delete(1.0, tk.END)
        self.details_text.delete(1.0, tk.END)

        if problem_reviews:
            # Статистика
            keyword_stats = {}
            for review in problem_reviews:
                for keyword in review['keywords'].split(', '):
                    keyword_stats[keyword] = keyword_stats.get(keyword, 0) + 1

            self.stats_text.insert(tk.END, f"Найдено отзывов с проблемными словами: {len(problem_reviews)}\n\n")
            self.stats_text.insert(tk.END, "СТАТИСТИКА ПО КЛЮЧЕВЫМ СЛОВАМ:\n")
            for keyword, count in sorted(keyword_stats.items(), key=lambda x: x[1], reverse=True):
                self.stats_text.insert(tk.END, f"  {keyword}: {count} отзывов\n")

            # Детали
            self.details_text.insert(tk.END, "ДЕТАЛЬНЫЙ АНАЛИЗ ОТЗЫВОВ:\n")
            self.details_text.insert(tk.END, "=" * 60 + "\n")

            for i, review in enumerate(problem_reviews[:15], 1):
                self.details_text.insert(tk.END, f"{i}. ⭐ {review['rating']} | {review['keywords']}\n")
                self.details_text.insert(tk.END, f"   Текст: {review['text']}\n")
                self.details_text.insert(tk.END, "-" * 50 + "\n")
        else:
            self.stats_text.insert(tk.END, "Отзывов с проблемными словами не найдено.")

    def update_sentiment_tab(self, sentiment_results):
        """Обновляем вкладку тональности"""
        self.sentiment_text.delete(1.0, tk.END)

        if sentiment_results:
            from collections import Counter
            sentiment_counts = Counter([r['sentiment'] for r in sentiment_results])

            total = len(sentiment_results)
            positive_pct = (sentiment_counts['positive'] / total) * 100
            neutral_pct = (sentiment_counts['neutral'] / total) * 100
            negative_pct = (sentiment_counts['negative'] / total) * 100

            self.sentiment_text.insert(tk.END, "РАСПРЕДЕЛЕНИЕ ТОНАЛЬНОСТИ:\n")
            self.sentiment_text.insert(tk.END, "=" * 40 + "\n\n")
            self.sentiment_text.insert(tk.END,
                                       f"✅ Положительные: {sentiment_counts['positive']} ({positive_pct:.1f}%)\n")
            self.sentiment_text.insert(tk.END, f"⚠️  Нейтральные: {sentiment_counts['neutral']} ({neutral_pct:.1f}%)\n")
            self.sentiment_text.insert(tk.END,
                                       f"❌ Отрицательные: {sentiment_counts['negative']} ({negative_pct:.1f}%)\n\n")

            self.sentiment_text.insert(tk.END, f"Всего проанализировано отзывов: {total}\n")
        else:
            self.sentiment_text.insert(tk.END, "Нет данных для анализа тональности.")

    def run(self):
        """Запускаем главный цикл"""
        self.root.mainloop()


def show_nltk_analysis(df):
    """Показываем GUI с анализом"""
    app = NLTAnalyzerGUI(df)
    app.run()