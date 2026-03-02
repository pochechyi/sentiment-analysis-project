import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from collections import defaultdict

def plot_dat(df):
    return 0


def plot_ratings1(df):
    """График: Распределение оценок по звездам"""
    plt.figure(figsize=(10, 6), num='Анализ - простейший оценок товаров')

    # Используем конкретные колонки из данных
    rating_col = 'Количество звезд'

    if rating_col in df.columns:
        # Преобразуем в числа и убираем пустые значения
        ratings = pd.to_numeric(df[rating_col], errors='coerce').dropna()

        if len(ratings) > 0:
            # Считаем количество каждой оценки
            rating_counts = ratings.value_counts().sort_index()

            # Создаем столбчатую диаграмму
            bars = plt.bar(rating_counts.index, rating_counts.values,
                           color='skyblue', edgecolor='black', alpha=0.7)

            # Добавляем подписи на столбцах
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width() / 2., height,
                         f'{int(height)}', ha='center', va='bottom')

            plt.title('Распределение оценок по звездам', fontsize=14, fontweight='bold')
            plt.xlabel('Количество звезд', fontsize=12)
            plt.ylabel('Количество отзывов', fontsize=12)
            plt.grid(axis='y', alpha=0.3)

        else:
            plt.text(0.5, 0.5, 'Нет данных об оценках',
                     ha='center', va='center', transform=plt.gca().transAxes, fontsize=12)

    else:
        plt.text(0.5, 0.5, f'Колонка "{rating_col}" не найдена',
                 ha='center', va='center', transform=plt.gca().transAxes, fontsize=12)

    plt.tight_layout()
    plt.savefig('reports/figures/ratings_distribution.png', dpi=300, bbox_inches='tight')
    plt.show()


def plot_ratings2(df):
    """График: Зависимость длины отзыва от оценки (scatter plot)"""
    plt.figure(figsize=(12, 8), num='Длина отзыва vs Оценка')

    # Используем конкретные колонки из данных
    text_col = 'Текст отзыва'
    rating_col = 'Количество звезд'

    if text_col in df.columns and rating_col in df.columns:
        # Очищаем данные
        df_clean = df[[text_col, rating_col]].copy()
        df_clean = df_clean.dropna()

        # Преобразуем оценки в числа
        df_clean[rating_col] = pd.to_numeric(df_clean[rating_col], errors='coerce')
        df_clean = df_clean.dropna()

        # Считаем длину отзыва в словах (количество слов)
        df_clean['длина_в_словах'] = df_clean[text_col].astype(str).apply(lambda x: len(x.split()))

        if len(df_clean) > 0:
            # Создаем цветовую карту в зависимости от оценки
            colors = ['#ff6b6b', '#ff9e44', '#ffd166', '#a8e6cf', '#4ecdc4']  # красный -> зеленый
            color_map = []

            for rating in df_clean[rating_col]:
                if rating == 1:
                    color_map.append(colors[0])
                elif rating == 2:
                    color_map.append(colors[1])
                elif rating == 3:
                    color_map.append(colors[2])
                elif rating == 4:
                    color_map.append(colors[3])
                else:
                    color_map.append(colors[4])

            # Scatter plot с цветами
            scatter = plt.scatter(df_clean[rating_col], df_clean['длина_в_словах'],
                                  alpha=0.7, s=60, c=color_map,
                                  edgecolors='black', linewidth=0.5)

            # Добавляем jitter для лучшей видимости
            jitter = np.random.normal(0, 0.08, len(df_clean))
            x_jittered = df_clean[rating_col] + jitter

            # Второй scatter с jitter (полупрозрачный для плотности)
            plt.scatter(x_jittered, df_clean['длина_в_словах'],
                        alpha=0.3, s=40, c=color_map)

            # Линия тренда (полиномиальная регрессия)
            z = np.polyfit(df_clean[rating_col], df_clean['длина_в_словах'], 2)  # 2 степень для кривой
            p = np.poly1d(z)

            # Создаем точки для гладкой линии тренда
            x_trend = np.linspace(df_clean[rating_col].min(), df_clean[rating_col].max(), 100)
            y_trend = p(x_trend)

            plt.plot(x_trend, y_trend, color='#d32f2f', linewidth=3, linestyle='--',
                     label=f'Линия тренда (R² = {np.corrcoef(df_clean[rating_col], df_clean["длина_в_словах"])[0, 1]:.3f})')

            # Настройки графика
            plt.title('Зависимость длины отзыва от оценки\n(Каждая точка - один отзыв)',
                      fontsize=14, fontweight='bold', pad=20)
            plt.xlabel('Количество звезд', fontsize=12, fontweight='bold')
            plt.ylabel('Длина отзыва (количество слов)', fontsize=12, fontweight='bold')

            # Легенда для цветов
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor=colors[0], label='⭐ 1 звезда'),
                Patch(facecolor=colors[1], label='⭐ 2 звезды'),
                Patch(facecolor=colors[2], label='⭐ 3 звезды'),
                Patch(facecolor=colors[3], label='⭐ 4 звезды'),
                Patch(facecolor=colors[4], label='⭐ 5 звезд')
            ]
            plt.legend(handles=legend_elements, loc='upper right')

            plt.grid(True, alpha=0.3)
            plt.xticks([1, 2, 3, 4, 5])

            # Добавляем boxplot для каждой оценки
            data_by_rating = [df_clean[df_clean[rating_col] == rating]['длина_в_словах']
                              for rating in sorted(df_clean[rating_col].unique())]

            positions = sorted(df_clean[rating_col].unique())
            boxplot = plt.boxplot(data_by_rating, positions=positions, widths=0.3,
                                  patch_artist=True, showfliers=False,
                                  boxprops=dict(facecolor='lightgray', alpha=0.7),
                                  medianprops=dict(color='red', linewidth=2))

            # Выводим статистику
            print(f"\n📊 СТАТИСТИКА ПО ОТЗЫВАМ:")
            print(f"Всего отзывов: {len(df_clean)}")
            print(f"Средняя длина отзыва: {df_clean['длина_в_словах'].mean():.1f} слов")
            print(f"Медианная длина: {df_clean['длина_в_словах'].median():.1f} слов")
            print(f"Коэффициент корреляции: {np.corrcoef(df_clean[rating_col], df_clean['длина_в_словах'])[0, 1]:.3f}")

            print(f"\n📈 СТАТИСТИКА ПО ОЦЕНКАМ:")
            for rating in sorted(df_clean[rating_col].unique()):
                subset = df_clean[df_clean[rating_col] == rating]
                print(f"⭐ {int(rating)} звезд: {len(subset)} отзывов")
                print(f"   Средняя длина: {subset['длина_в_словах'].mean():.1f} слов")
                print(f"   Медиана: {subset['длина_в_словах'].median():.1f} слов")
                print(f"   Стандартное отклонение: {subset['длина_в_словах'].std():.1f} слов")
                print()

        else:
            plt.text(0.5, 0.5, 'Нет данных для построения графика',
                     ha='center', va='center', transform=plt.gca().transAxes, fontsize=12)

    else:
        plt.text(0.5, 0.5, 'Не найдены необходимые колонки',
                 ha='center', va='center', transform=plt.gca().transAxes, fontsize=12)

    plt.tight_layout()
    plt.savefig('reports/figures/length_vs_rating_scatter.png', dpi=300, bbox_inches='tight')
    plt.show()


def plot_seasonal_ratings(df):
    # Используем конкретные колонки из данных
    rating_col = 'Количество звезд'
    date_col = None

    # Ищем колонку с датами
    for col in df.columns:
        if 'дата' in col.lower() or 'date' in col.lower() or 'время' in col.lower():
            date_col = col
            break

    if date_col and rating_col in df.columns:
        # Очищаем данные
        df_clean = df[[date_col, rating_col]].copy()
        df_clean = df_clean.dropna()

        # Преобразуем оценки в числа
        df_clean[rating_col] = pd.to_numeric(df_clean[rating_col], errors='coerce')
        df_clean = df_clean.dropna()

        # Преобразуем даты
        try:
            df_clean[date_col] = pd.to_datetime(df_clean[date_col], errors='coerce')
            df_clean = df_clean.dropna()
        except:
            print("❌ Ошибка при преобразовании дат")
            return

        if len(df_clean) > 0:
            # Создаем дополнительные временные колонки
            df_clean['год'] = df_clean[date_col].dt.year
            df_clean['месяц'] = df_clean[date_col].dt.month
            df_clean['год_месяц'] = df_clean[date_col].dt.to_period('M')
            df_clean['квартал'] = df_clean[date_col].dt.quarter
            df_clean['сезон'] = df_clean['месяц'].map({
                12: 'Зима', 1: 'Зима', 2: 'Зима',
                3: 'Весна', 4: 'Весна', 5: 'Весна',
                6: 'Лето', 7: 'Лето', 8: 'Лето',
                9: 'Осень', 10: 'Осень', 11: 'Осень'
            })

            # Получаем диапазон годов и месяцев
            years = sorted(df_clean['год'].unique())
            months_ru = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн',
                         'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']

            # Создаем подграфики - теперь только 2 графика
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 6))

            # 1. ГРАФИК: Хронологический по месяцам и годам
            # Группируем по году и месяцу
            chronological_data = df_clean.groupby('год_месяц')[rating_col].agg(['mean', 'count', 'std']).reset_index()
            chronological_data['год_месяц_str'] = chronological_data['год_месяц'].astype(str)

            # Сортируем по дате
            chronological_data = chronological_data.sort_values('год_месяц')

            # Создаем подписи для оси X
            x_labels = []
            for period in chronological_data['год_месяц']:
                year = period.year
                month = period.month
                x_labels.append(f"{months_ru[month - 1]}\n{year}")

            x_pos = np.arange(len(chronological_data))

            # Создаем цветовую схему по годам
            unique_years = sorted(df_clean['год'].unique())
            year_colors = plt.cm.Set3(np.linspace(0, 1, len(unique_years)))
            color_map = {year: color for year, color in zip(unique_years, year_colors)}

            bars = ax1.bar(x_pos, chronological_data['mean'],
                           color=[color_map[p.year] for p in chronological_data['год_месяц']],
                           alpha=0.8, edgecolor='black', width=0.7)

            # Добавляем значения на столбцы
            for i, (bar, avg, count, std) in enumerate(zip(bars, chronological_data['mean'],
                                                           chronological_data['count'], chronological_data['std'])):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width() / 2., height + 0.1,
                         f'{avg:.2f}\n(n={int(count)})',
                         ha='center', va='bottom', fontsize=7, fontweight='bold')

            ax1.set_title('Средние оценки по месяцам\n(хронологический порядок)', fontsize=14, fontweight='bold')
            ax1.set_xlabel('Месяц и год', fontsize=12)
            ax1.set_ylabel('Средняя оценка', fontsize=12)
            ax1.set_xticks(x_pos)
            ax1.set_xticklabels(x_labels, rotation=45, ha='right')
            ax1.grid(True, alpha=0.3)
            ax1.set_ylim(0, 5.8)

            # Добавляем легенду для годов
            legend_elements = [plt.Rectangle((0, 0), 1, 1, color=color_map[year], alpha=0.8,
                                             label=f'{year}') for year in unique_years]
            ax1.legend(handles=legend_elements, title='Год', loc='upper right', fontsize=9)

            # 2. ГРАФИК: По сезонам с разбивкой по годам и общей статистикой
            seasonal_avg = df_clean.groupby(['сезон', 'год'])[rating_col].mean().unstack()
            seasonal_count = df_clean.groupby(['сезон', 'год'])[rating_col].count().unstack()

            # Правильный порядок сезонов
            season_order = ['Зима', 'Весна', 'Лето', 'Осень']
            seasonal_avg = seasonal_avg.reindex(season_order)
            seasonal_count = seasonal_count.reindex(season_order)

            colors_season = ['#6baed6', '#74c476', '#fd8d3c', '#e6550d']

            # Для группированного графика
            x_pos_season = np.arange(len(season_order))
            width_season = 0.8 / len(years) if len(years) > 0 else 0.4

            for i, year in enumerate(years):
                if year in seasonal_avg.columns:
                    offset = width_season * i - width_season * (len(years) - 1) / 2
                    bars = ax2.bar(x_pos_season + offset, seasonal_avg[year], width_season,
                                   label=f'{year}', alpha=0.8, edgecolor='black')

                    # Добавляем значения
                    for j, (bar, avg, count) in enumerate(zip(bars, seasonal_avg[year], seasonal_count[year])):
                        if not np.isnan(avg):
                            height = bar.get_height()
                            ax2.text(bar.get_x() + bar.get_width() / 2., height + 0.05,
                                     f'{avg:.2f}\n(n={int(count)})', ha='center', va='bottom',
                                     fontsize=8, fontweight='bold')

            # Добавляем общие средние по сезонам (все года)
            seasonal_all_avg = df_clean.groupby('сезон')[rating_col].mean().reindex(season_order)
            for i, season in enumerate(season_order):
                if season in seasonal_all_avg.index:
                    ax2.axhline(y=seasonal_all_avg[season], xmin=(i - 0.4) / len(season_order),
                                xmax=(i + 0.4) / len(season_order), color='red', linestyle='--',
                                linewidth=2, alpha=0.8, label='Общее среднее' if i == 0 else "")

            ax2.set_title('Средние оценки по сезонам\n(разбивка по годам)', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Сезон', fontsize=12)
            ax2.set_ylabel('Средняя оценка', fontsize=12)
            ax2.set_xticks(x_pos_season)
            ax2.set_xticklabels(season_order)
            ax2.legend(title='Год')
            ax2.grid(True, alpha=0.3)
            ax2.set_ylim(0, 5.8)

            plt.tight_layout()

            # РАСШИРЕННАЯ СТАТИСТИКА
            print(f"\n📊 ДЕТАЛЬНАЯ СТАТИСТИКА ПО ВРЕМЕНИ:")
            print(
                f"Период данных: {df_clean[date_col].min().strftime('%d.%m.%Y')} - {df_clean[date_col].max().strftime('%d.%m.%Y')}")
            print(f"Всего отзывов с датами: {len(df_clean)}")
            print(f"Годы в данных: {', '.join(map(str, years))}")

            print(f"\n📈 ОБЩИЕ СРЕДНИЕ ОЦЕНКИ ПО СЕЗОНАМ:")
            seasonal_all_avg = df_clean.groupby('сезон')[rating_col].mean()
            seasonal_all_count = df_clean.groupby('сезон')[rating_col].count()
            seasonal_all_std = df_clean.groupby('сезон')[rating_col].std()

            for season in season_order:
                if season in seasonal_all_avg.index:
                    avg = seasonal_all_avg[season]
                    count = seasonal_all_count[season]
                    std = seasonal_all_std[season]
                    print(f"🎯 {season}: {avg:.2f} ± {std:.2f} (n={count})")

            print(f"\n📅 ХРОНОЛОГИЧЕСКАЯ СТАТИСТИКА ПО МЕСЯЦАМ:")
            print("\nПериод       | Среднее | Кол-во | Станд.отклон.")
            print("-" * 50)

            for idx, row in chronological_data.iterrows():
                period_str = f"{months_ru[row['год_месяц'].month - 1]} {row['год_месяц'].year}"
                print(f"{period_str:12} | {row['mean']:7.2f} | {int(row['count']):6} | {row['std']:.2f}")

            print(f"\n🏆 САМЫЕ УСПЕШНЫЕ ПЕРИОДЫ:")
            # Лучшие месяцы по хронологии
            top_periods = chronological_data.nlargest(3, 'mean')
            for idx, row in top_periods.iterrows():
                period_str = f"{months_ru[row['год_месяц'].month - 1]} {row['год_месяц'].year}"
                print(f"🏆 {period_str}: {row['mean']:.2f} (n={int(row['count'])}, σ={row['std']:.2f})")

            # Лучшие сезоны
            top_seasons = seasonal_all_avg.nlargest(2)
            for season, avg in top_seasons.items():
                season_data = df_clean[df_clean['сезон'] == season][rating_col]
                print(f"🏆 Сезон {season}: {avg:.2f} (n={len(season_data)}, σ={season_data.std():.2f})")

            print(f"\n📉 САМЫЕ ПРОБЛЕМНЫЕ ПЕРИОДЫ:")
            # Худшие месяцы по хронологии
            bottom_periods = chronological_data.nsmallest(3, 'mean')
            for idx, row in bottom_periods.iterrows():
                period_str = f"{months_ru[row['год_месяц'].month - 1]} {row['год_месяц'].year}"
                print(f"⚠️  {period_str}: {row['mean']:.2f} (n={int(row['count'])}, σ={row['std']:.2f})")

            # Худшие сезоны
            bottom_seasons = seasonal_all_avg.nsmallest(2)
            for season, avg in bottom_seasons.items():
                season_data = df_clean[df_clean['сезон'] == season][rating_col]
                print(f"⚠️  Сезон {season}: {avg:.2f} (n={len(season_data)}, σ={season_data.std():.2f})")

            # Статистика по годам
            print(f"\n📅 ОБЩАЯ СТАТИСТИКА ПО ГОДАМ:")
            yearly_stats = df_clean.groupby('год')[rating_col].agg(['mean', 'count', 'std'])
            for year, stats in yearly_stats.iterrows():
                print(f"📅 {year}: {stats['mean']:.2f} ± {stats['std']:.2f} (n={stats['count']})")

        else:
            plt.figure(figsize=(10, 6))
            plt.text(0.5, 0.5, 'Нет данных для построения графика',
                     ha='center', va='center', transform=plt.gca().transAxes, fontsize=12)

    else:
        plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, 'Не найдены колонки с датами или оценками',
                 ha='center', va='center', transform=plt.gca().transAxes, fontsize=12)

    plt.tight_layout()
    plt.savefig('reports/figures/seasonal_ratings.png', dpi=300, bbox_inches='tight')
    plt.show()
def calculate_nps(df):
    """Расчет Net Promoter Score"""
    promoters = len(df[df['Оценка'] >= 4])  # 4-5 звезд
    detractors = len(df[df['Оценка'] <= 2])  # 1-2 звезды
    total = len(df)

    if total > 0:
        nps = (promoters - detractors) / total * 100
        return round(nps, 1)
    return 0

def plot_review_length_chars_vs_rating(df):
    """График: Зависимость длины отзыва в символах от оценки"""
    plt.figure(figsize=(12, 8), num='Длина отзыва (символы) vs Оценка')

    text_col = 'Текст отзыва'
    rating_col = 'Количество звезд'

    if text_col in df.columns and rating_col in df.columns:
        df_clean = df[[text_col, rating_col]].copy().dropna()

        # Длина в символах
        df_clean['длина_в_символах'] = df_clean[text_col].astype(str).apply(len)

        if len(df_clean) > 0:
            plt.scatter(df_clean[rating_col], df_clean['длина_в_символах'],
                        alpha=0.6, s=50, color='green')

            plt.title('Зависимость длины отзыва от оценки\n(Длина в символах)',
                      fontsize=14, fontweight='bold')
            plt.xlabel('Количество звезд', fontsize=12)
            plt.ylabel('Длина отзыва (количество символов)', fontsize=12)
            plt.grid(True, alpha=0.3)

            print(f"\nСтатистика по символам:")
            print(f"Средняя длина: {df_clean['длина_в_символах'].mean():.0f} символов")

        else:
            plt.text(0.5, 0.5, 'Нет данных', ha='center', va='center', fontsize=12)

    plt.tight_layout()
    plt.savefig('reports/figures/length_chars_vs_rating.png', dpi=300, bbox_inches='tight')
    plt.show()


def plot_low_rating_categories(df):
    """Диаграмма: Тематика отзывов с оценкой 1-2 звезды"""

    text_col = 'Текст отзыва'
    rating_col = 'Количество звезд'

    if text_col not in df.columns or rating_col not in df.columns:
        plt.text(0.5, 0.5, 'Не найдены необходимые колонки',
                 ha='center', va='center', transform=plt.gca().transAxes, fontsize=12)
        plt.tight_layout()
        plt.savefig('reports/figures/low_rating_categories.png', dpi=300, bbox_inches='tight')
        plt.show()
        return None, None

    # Фильтруем отзывы с оценкой 1-2 звезды
    low_ratings = df[df[rating_col].isin([1, 2])].copy()

    if len(low_ratings) == 0:
        plt.text(0.5, 0.5, 'Нет отзывов с оценкой 1-2 звезды',
                 ha='center', va='center', transform=plt.gca().transAxes, fontsize=14)
        plt.tight_layout()
        plt.savefig('reports/figures/low_rating_categories.png', dpi=300, bbox_inches='tight')
        plt.show()
        return None, None

    # Категории и ключевые слова
    categories = {
        'Качество': ['качеств', 'некачествен', 'брак', 'дефект', 'поломк', 'сломан'],
        'Цена': ['дорог', 'цен', 'переплат', 'наценк', 'стоимост', 'денег'],
        'Доставка': ['доставк', 'почт', 'курьер', 'получен', 'отправк', 'срок'],
        'Обслуживание': ['обслуж', 'консульт', 'продавец', 'менеджер', 'поддержк']
    }

    # Анализируем каждый отзыв
    category_counts = defaultdict(int)

    for idx, row in low_ratings.iterrows():
        review_text = str(row[text_col]).lower()
        found_categories = []

        # Проверяем каждую категорию
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in review_text:
                    found_categories.append(category)
                    break

        # Если нашли категории - добавляем в статистику
        if found_categories:
            for category in found_categories:
                category_counts[category] += 1

    # Если нет отзывов, попадающих в категории
    if len(category_counts) == 0:
        plt.text(0.5, 0.5, 'Нет отзывов, попадающих в заданные категории',
                 ha='center', va='center', transform=plt.gca().transAxes, fontsize=14)
        plt.tight_layout()
        plt.savefig('reports/figures/low_rating_categories.png', dpi=300, bbox_inches='tight')
        plt.show()
        return None, None

    # Сортируем категории по количеству отзывов
    sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
    categories_names = [cat[0] for cat in sorted_categories]
    categories_counts = [cat[1] for cat in sorted_categories]

    # Цвета для категорий
    colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57']

    # Создаем диаграмму
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # 1. Круговая диаграмма
    wedges, texts, autotexts = ax1.pie(categories_counts, labels=categories_names, autopct='%1.1f%%',
                                       colors=colors[:len(categories_names)], startangle=90)
    ax1.set_title('Распределение по категориям\n(отзывы 1-2 звезды)', fontsize=14, fontweight='bold')

    # 2. Столбчатая диаграмма
    bars = ax2.bar(categories_names, categories_counts, color=colors[:len(categories_names)], alpha=0.7)
    ax2.set_title('Количество отзывов по категориям', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Категории')
    ax2.set_ylabel('Количество отзывов')
    ax2.tick_params(axis='x', rotation=45)

    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2., height,
                 f'{int(height)}', ha='center', va='bottom')

    # Общая статистика
    total_reviews = len(low_ratings)
    categorized_reviews = sum(categories_counts)

    plt.suptitle(f'Анализ отзывов с низкими оценками (1-2 звезды)\nВсего отзывов: {total_reviews} (охвачено: {categorized_reviews})',
                 fontsize=16, fontweight='bold')

    plt.tight_layout()
    plt.savefig('reports/figures/low_rating_categories.png', dpi=300, bbox_inches='tight')
    plt.show()

    # Выводим статистику в консоль
    print(f"\nВсего отзывов 1-2 звезды: {total_reviews}")
    print(f"Охвачено категориями: {categorized_reviews} ({categorized_reviews/total_reviews*100:.1f}%)")
    for category, count in sorted_categories:
        print(f"📊 {category}: {count} отзывов")

    return category_counts, {}

def analyze_problem_reviews(df):
    """Анализ отзывов с проблемными словами"""
    # Ключевые слова для поиска проблем
    problem_keywords = {
        'брак': ['брак', 'бракован'],
        'качество': ['качеств', 'некачествен'],
        'отказ': ['отказ', 'отказыва'],
        'возврат': ['возврат', 'вернут'],
        'разочарование': ['разочарован'],
        'проблема': ['проблем'],
        'дефект': ['дефект'],
        'недостаток': ['недостаток'],
        'обидно': ['обидно'],
        'не понравилось': ['не понрави'],
        'позорище': ['позор']
    }

    text_col = 'Текст отзыва'
    rating_col = 'Количество звезд'

    if text_col not in df.columns:
        print("Колонка с текстом отзывов не найдена!")
        return []

    print("=" * 60)
    print("АНАЛИЗ ОТЗЫВОВ С ПРОБЛЕМНЫМИ СЛОВАМИ")
    print("=" * 60)

    problem_reviews = []

    for idx, row in df.iterrows():
        review_text = str(row[text_col]).lower()
        rating = row[rating_col] if rating_col in df.columns else 'N/A'

        found_keywords = []

        # Ищем ключевые слова в тексте
        for category, keywords in problem_keywords.items():
            for keyword in keywords:
                if keyword in review_text:
                    found_keywords.append(category)
                    break

        if found_keywords:
            problem_reviews.append({
                'id': idx,
                'rating': rating,
                'keywords': ', '.join(found_keywords),
                'text': str(row[text_col])[:150] + '...' if len(str(row[text_col])) > 150 else str(row[text_col])
            })

    # Выводим результаты
    if problem_reviews:
        print(f"Найдено отзывов с проблемными словами: {len(problem_reviews)}")

        # Статистика по ключевым словам
        keyword_stats = {}
        for review in problem_reviews:
            for keyword in review['keywords'].split(', '):
                keyword_stats[keyword] = keyword_stats.get(keyword, 0) + 1

        print("\n📊 СТАТИСТИКА ПО КЛЮЧЕВЫМ СЛОВАМ:")
        for keyword, count in sorted(keyword_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  {keyword}: {count} отзывов")

        print("\n📝 ПРИМЕРЫ ОТЗЫВОВ:")
        for i, review in enumerate(problem_reviews[:10], 1):
            print(f"{i}. ⭐ {review['rating']} | {review['keywords']}")
            print(f"   {review['text']}")
            print("-" * 50)

    else:
        print("Отзывов с проблемными словами не найдено.")

    return problem_reviews