# main.py
from src.loader import load_data
from src.visualization import plot_ratings1, plot_ratings2, plot_low_rating_categories, plot_seasonal_ratings
from src.text_analyzer import analyze_problem_reviews_nltk
from src.gui_analyzer import show_nltk_analysis
from src.dashboard import BusinessDashboard, run_streamlit_dashboard
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os


def calculate_business_metrics(df):

    analyzer = BusinessDashboard(df)
    metrics = analyzer.calculate_key_metrics()
    issues = analyzer.identify_critical_issues()

    # Вывод метрик
    print(f"📈 Общее количество отзывов: {metrics['total_reviews']}")
    print(f"⭐ Средняя оценка: {metrics['avg_rating']:.2f}/5")
    print(
        f"✅ Положительные отзывы (4-5 звезд): {metrics['positive_reviews']} ({metrics['positive_reviews'] / metrics['total_reviews'] * 100:.1f}%)")
    print(
        f"❌ Негативные отзывы (1-2 звезд): {metrics['negative_reviews']} ({metrics['negative_reviews'] / metrics['total_reviews'] * 100:.1f}%)")
    print(f"🎯 NPS-показатель: {metrics['nps']:.1f}")

    # Анализ критических проблем
    print(f"\n🔍 КРИТИЧЕСКИЕ ПРОБЛЕМЫ:")
    for problem, count in sorted(issues.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"   - {problem}: {count} упоминаний")

    # Объяснение выбора проблем
    print(f"\n🤔 ПОЧЕМУ ЭТИ ПРОБЛЕМЫ ВАЖНЫ:")
    print("   - Проблемы с КАЧЕСТВОМ напрямую влияют на лояльность клиентов")
    print("   - НЕСООТВЕТСТВИЕ ОПИСАНИЮ приводит к возвратам")
    print("   - БРАК увеличивает затраты и репутационные риски")
    print("   - КОМПЛЕКТАЦИЯ - технические ошибки, которые легко исправить")

    return metrics





def main():
    print("Начинаем анализ оценок...")

    try:
        # Создаем папку для графиков
        os.makedirs('reports/figures', exist_ok=True)

        # Загружаем данные
        df = load_data()

        print(f"\nКолонки в данных: {list(df.columns)}")

        # Существующие графики
        print("\n1. Создаем график распределения оценок...")
        plot_ratings1(df)

        print("\n2. Зависимость длины отзыва от оценки...")
        plot_ratings2(df)

        print("\n3. Анализ негативных отзывов...")
        plot_low_rating_categories(df)

        plot_seasonal_ratings(df)

        print("\n4. NLTK анализ отзывов...")
        analyze_problem_reviews_nltk(df)

        print("\n5. 📊 БИЗНЕС-МЕТРИКИ ДЛЯ КЛИЕНТА...")
        metrics = calculate_business_metrics(df)

        print("\n6. 🎛️ ИНТЕРАКТИВНЫЙ ДАШБОРД...")
        print("Запуск Streamlit дашборда...")
        print("Для запуска выполните в терминале: streamlit run src/dashboard.py")


        print("\n🎉 Анализ завершен успешно!")

    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")
        print("Проверьте наличие необходимых файлов и структуру данных")


if __name__ == "__main__":
    main()