# src/simple_metrics.py
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def calculate_simple_metrics(df):
    """Простой расчет бизнес-метрик"""

    print("📊 БИЗНЕС-МЕТРИКИ ДЛЯ КЛИЕНТА")
    print("=" * 50)

    # Базовые метрики
    total = len(df)
    print(f"• Всего отзывов: {total}")

    if 'Оценка' in df.columns:
        avg_rating = df['Оценка'].mean()
        print(f"• Средняя оценка: {avg_rating:.2f}/5")

        # NPS расчет
        promoters = len(df[df['Оценка'] >= 4])
        detractors = len(df[df['Оценка'] <= 2])
        nps = (promoters - detractors) / total * 100
        print(f"• NPS: {nps:.1f} пунктов")

        # Распределение оценок
        print(f"\n⭐ РАСПРЕДЕЛЕНИЕ ОЦЕНОК:")
        for rating in [5, 4, 3, 2, 1]:
            count = len(df[df['Оценка'] == rating])
            percentage = (count / total * 100) if total > 0 else 0
            print(f"  {rating} звезд: {count} отзывов ({percentage:.1f}%)")

    if 'Текст отзыва' in df.columns and 'Оценка' in df.columns:
        # Анализ проблем в негативных отзывах
        negative_reviews = df[df['Оценка'] <= 3]['Текст отзыва'].dropna()

        problems = {
            'качество': negative_reviews.astype(str).str.contains('качеств|брак|слом|плох', case=False, na=False).sum(),
            'доставка': negative_reviews.astype(str).str.contains('доставк|курьер|ждал|опозда', case=False,
                                                                  na=False).sum(),
            'цена': negative_reviews.astype(str).str.contains('дорог|цен|переплат|стоим', case=False, na=False).sum(),
            'сервис': negative_reviews.astype(str).str.contains('сервис|обслуживан|менеджер|поддерж', case=False,
                                                                na=False).sum(),
        }

        print(f"\n🚨 ОСНОВНЫЕ ПРОБЛЕМЫ (в негативных отзывах):")
        for problem, count in problems.items():
            if count > 0:
                print(f"• {problem}: {count} упоминаний")

    # Рекомендации
    print(f"\n💡 РЕКОМЕНДАЦИИ:")
    if 'Оценка' in df.columns:
        if avg_rating < 3:
            print("• СРОЧНО: Низкая удовлетворенность - анализируйте негативные отзывы")
        elif avg_rating < 4:
            print("• ВАЖНО: Средняя удовлетворенность - работайте над улучшением сервиса")
        else:
            print("• ОТЛИЧНО: Высокая удовлетворенность - поддерживайте качество!")

    return total


def create_simple_dashboard(df):
    """Простой дашборд с метриками - УПРОЩЕННАЯ ВЕРСИЯ"""

    if 'Оценка' not in df.columns:
        print("❌ Нет данных об оценках для построения дашборда")
        return

    print("🔄 Создаем дашборд...")

    # Создаем один большой график вместо нескольких
    plt.figure(figsize=(12, 8))

    # 1. Основной график - распределение оценок
    plt.subplot(2, 2, 1)
    rating_counts = df['Оценка'].value_counts().sort_index()
    colors = ['#ff4444', '#ff8c00', '#ffd700', '#90ee90', '#008000']
    bars = plt.bar(rating_counts.index, rating_counts.values, color=colors, alpha=0.8)
    plt.title('Распределение оценок', fontweight='bold')
    plt.xlabel('Оценка')
    plt.ylabel('Количество')

    # Добавляем числа на столбцы
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., height + 0.1,
                 f'{int(height)}', ha='center', va='bottom')

    # 2. Средняя оценка
    plt.subplot(2, 2, 2)
    avg_rating = df['Оценка'].mean()
    plt.bar(['Средняя'], [avg_rating], color='#2196F3', alpha=0.7)
    plt.ylim(0, 5)
    plt.title(f'Средняя оценка: {avg_rating:.2f}/5', fontweight='bold')
    plt.text(0, avg_rating + 0.1, f'{avg_rating:.2f}', ha='center', va='bottom',
             fontweight='bold')

    # 3. NPS
    plt.subplot(2, 2, 3)
    promoters = len(df[df['Оценка'] >= 4])
    detractors = len(df[df['Оценка'] <= 2])
    total = len(df)
    nps = (promoters - detractors) / total * 100 if total > 0 else 0

    labels = ['Промоутеры', 'Нейтральные', 'Критики']
    sizes = [promoters, total - promoters - detractors, detractors]
    colors_nps = ['#4CAF50', '#FFC107', '#F44336']

    plt.pie(sizes, labels=labels, colors=colors_nps, autopct='%1.1f%%', startangle=90)
    plt.title(f'NPS: {nps:.1f}', fontweight='bold')

    # 4. Доля негативных
    plt.subplot(2, 2, 4)
    negative_count = len(df[df['Оценка'] <= 2])
    negative_pct = (negative_count / total * 100) if total > 0 else 0

    plt.pie([100 - negative_pct, negative_pct],
            labels=['Положительные', 'Негативные'],
            colors=['#4CAF50', '#F44336'],
            autopct='%1.1f%%', startangle=90)
    plt.title(f'Негативные: {negative_pct:.1f}%', fontweight='bold')

    plt.tight_layout()

    # СОХРАНЯЕМ И ПОКАЗЫВАЕМ
    plt.savefig('reports/figures/business_metrics.png', dpi=300, bbox_inches='tight')
    print("✅ График сохранен!")

    # ПРИНУДИТЕЛЬНЫЙ ПОКАЗ
    plt.show(block=True)
    print("📊 График открыт!")