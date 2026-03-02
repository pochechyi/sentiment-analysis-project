# metrics_calculator.py
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def calculate_business_metrics(df):
    """Расчет ключевых бизнес-метрик"""

    # Определяем колонки
    rating_col = 'Оценка'
    text_col = 'Текст отзыва'

    # Базовые метрики
    total_reviews = len(df)
    negative_reviews = len(df[df[rating_col] <= 2]) if rating_col in df.columns else 0

    metrics = {
        'total_reviews': total_reviews,
        'daily_csat': df[rating_col].mean() if rating_col in df.columns else 0,
        'daily_nps': calculate_nps(df),
        'negative_reviews_count': negative_reviews,
        'negative_reviews_pct': (negative_reviews / total_reviews * 100) if total_reviews > 0 else 0,
        'top_problems': get_top_problems(df),
    }

    return metrics


def calculate_nps(df):
    """Расчет Net Promoter Score"""
    rating_col = 'Оценка'
    if rating_col not in df.columns:
        return 0

    promoters = len(df[df[rating_col] >= 4])
    detractors = len(df[df[rating_col] <= 2])
    total = len(df)

    if total > 0:
        nps = (promoters - detractors) / total * 100
        return round(nps, 1)
    return 0


def get_top_problems(df, top_n=5):
    """Анализ топ проблем из отзывов"""
    rating_col = 'Оценка'
    text_col = 'Текст отзыва'

    if rating_col not in df.columns or text_col not in df.columns:
        return {}

    negative_reviews = df[df[rating_col] <= 3][text_col].dropna()

    problem_keywords = {
        'качество': ['качеств', 'брак', 'слом', 'неработ', 'плох'],
        'доставка': ['доставк', 'курьер', 'ждал', 'опозда', 'получен'],
        'цена': ['дорог', 'цен', 'стоим', 'переплат', 'дешев'],
        'сервис': ['сервис', 'обслуживан', 'консульт', 'менеджер', 'поддержк'],
    }

    problem_counts = {}

    for review in negative_reviews:
        review_text = str(review).lower()
        for problem, keywords in problem_keywords.items():
            if any(keyword in review_text for keyword in keywords):
                problem_counts[problem] = problem_counts.get(problem, 0) + 1

    return dict(sorted(problem_counts.items(), key=lambda x: x[1], reverse=True)[:top_n])


def create_business_dashboard(df):
    """Дашборд ключевых бизнес-метрик"""
    try:
        metrics = calculate_business_metrics(df)

        fig, axes = plt.subplots(2, 2, figsize=(15, 10))

        # 1. NPS
        axes[0, 0].pie([max(metrics['daily_nps'] + 100, 0), max(100 - (metrics['daily_nps'] + 100), 0)],
                       colors=['#4CAF50', '#f0f0f0'], startangle=90)
        axes[0, 0].add_artist(plt.Circle((0, 0), 0.7, fc='white'))
        axes[0, 0].text(0, 0, f"NPS\n{metrics['daily_nps']}", ha='center', va='center', fontsize=14, fontweight='bold')
        axes[0, 0].set_title('Net Promoter Score', fontweight='bold')

        # 2. CSAT
        axes[0, 1].bar(['CSAT'], [metrics['daily_csat']], color='#2196F3')
        axes[0, 1].set_ylim(0, 5)
        axes[0, 1].set_ylabel('Средняя оценка')
        axes[0, 1].set_title('Customer Satisfaction', fontweight='bold')
        axes[0, 1].text(0, metrics['daily_csat'] + 0.1, f'{metrics["daily_csat"]:.2f}',
                        ha='center', va='bottom', fontweight='bold')

        # 3. Негативные отзывы
        axes[1, 0].bar(['Негативные'], [metrics['negative_reviews_pct']], color='#FF5252')
        axes[1, 0].set_ylabel('Процент отзывов')
        axes[1, 0].set_title('Доля негативных отзывов', fontweight='bold')
        axes[1, 0].text(0, metrics['negative_reviews_pct'] + 1, f'{metrics["negative_reviews_pct"]:.1f}%',
                        ha='center', va='bottom', fontweight='bold')

        # 4. Топ проблемы
        problems = metrics['top_problems']
        if problems:
            problem_names = list(problems.keys())
            problem_counts = list(problems.values())
            axes[1, 1].barh(problem_names, problem_counts, color='#FF9800')
        else:
            axes[1, 1].text(0.5, 0.5, 'Нет данных', ha='center', va='center', transform=axes[1, 1].transAxes)
        axes[1, 1].set_title('Основные проблемы', fontweight='bold')
        axes[1, 1].set_xlabel('Количество')

        plt.tight_layout()
        plt.savefig('reports/figures/business_dashboard.png', dpi=300, bbox_inches='tight')
        plt.show()

        return metrics

    except Exception as e:
        print(f"Ошибка при создании дашборда: {e}")
        return {}


def generate_business_report(df):
    """Генерация бизнес-отчета"""
    metrics = calculate_business_metrics(df)

    print("📊 БИЗНЕС-ОТЧЕТ")
    print("=" * 40)
    print(f"Всего отзывов: {metrics['total_reviews']}")
    print(f"NPS: {metrics['daily_nps']} пунктов")
    print(f"Удовлетворенность: {metrics['daily_csat']:.2f}/5")
    print(f"Негативные отзывы: {metrics['negative_reviews_count']} ({metrics['negative_reviews_pct']:.1f}%)")

    print("\n🚨 ОСНОВНЫЕ ПРОБЛЕМЫ:")
    for problem, count in metrics['top_problems'].items():
        print(f"• {problem}: {count} упоминаний")