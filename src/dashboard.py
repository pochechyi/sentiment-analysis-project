# src/dashboard.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np
from textblob import TextBlob
import streamlit as st
import warnings
from datetime import datetime, timedelta, date

warnings.filterwarnings('ignore')


class BusinessDashboard:
    def __init__(self, df):
        self.df = df.copy()
        self.column_names = self.detect_column_names()
        self.setup_data()

    def create_metrics_dashboard(self, period_data=None):
        """Создание дашборда с основными метриками"""
        if period_data is None:
            period_data = self.df

        metrics = self.calculate_key_metrics(period_data)

        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('ОСНОВНЫЕ БИЗНЕС-МЕТРИКИ', fontsize=16, fontweight='bold')

        # 1. Распределение оценок
        if not metrics['rating_distribution'].empty:
            axes[0, 0].pie(metrics['rating_distribution'].values,
                           labels=metrics['rating_distribution'].index,
                           autopct='%1.1f%%', startangle=90)
            axes[0, 0].set_title('Распределение оценок')

        # 2. NPS метрика
        nps_data = [metrics['positive_reviews'], metrics['neutral_reviews'], metrics['negative_reviews']]
        nps_labels = ['Промоутеры', 'Нейтральные', 'Критики']
        axes[0, 1].bar(nps_labels, nps_data, color=['green', 'gray', 'red'])
        axes[0, 1].set_title('NPS Сегментация')
        axes[0, 1].tick_params(axis='x', rotation=45)

        # 3. Ключевые показатели
        key_metrics = {
            'NPS': metrics['nps'],
            'CSAT': metrics['csat'],
            'Ср.оценка': metrics['avg_rating']
        }
        axes[1, 0].bar(key_metrics.keys(), key_metrics.values(), color=['blue', 'orange', 'purple'])
        axes[1, 0].set_title('Ключевые показатели')
        axes[1, 0].tick_params(axis='x', rotation=45)

        # 4. Сводная информация
        axes[1, 1].axis('off')
        info_text = f"""
        Всего отзывов: {metrics['total_reviews']}
        Позитивных: {metrics['positive_reviews']}
        Нейтральных: {metrics['neutral_reviews']}
        Негативных: {metrics['negative_reviews']}
        Доля негативных: {metrics['negative_ratio']:.1f}%
        """
        axes[1, 1].text(0.1, 0.9, info_text, fontsize=12, verticalalignment='top')

        plt.tight_layout()
        return fig

    def detect_column_names(self):
        """Автоматическое определение названий колонок"""
        column_mapping = {}

        # Поиск колонок по паттернам
        for col in self.df.columns:
            col_lower = col.lower()

            if any(word in col_lower for word in ['id', 'номер', 'код']):
                column_mapping['id'] = col
            elif any(word in col_lower for word in ['дата', 'date']):
                column_mapping['date'] = col
            elif any(word in col_lower for word in ['звезд', 'star', 'рейтинг', 'rating', 'оценк']):
                column_mapping['rating'] = col
            elif any(word in col_lower for word in ['бренд', 'brand', 'производитель']):
                column_mapping['brand'] = col
            elif any(word in col_lower for word in ['текст', 'text', 'отзыв', 'review', 'комментарий']):
                column_mapping['text'] = col
            elif any(word in col_lower for word in ['номенклатур', 'артикул', 'товар', 'product']):
                column_mapping['product'] = col

        print(f"🔍 Обнаруженные колонки: {column_mapping}")
        return column_mapping

    def setup_data(self):
        """Подготовка данных для анализа"""
        # Очистка и преобразование данных
        if 'date' in self.column_names:
            date_col = self.column_names['date']
            # Сохраняем оригинальные даты для отладки
            self.df['date_original'] = self.df[date_col]

            print(f"📅 Примеры исходных дат: {self.df[date_col].head(10).tolist()}")

            # Пробуем разные форматы дат последовательно
            date_formats = [
                '%d/%m/%Y',  # 01/09/2020 (день/месяц/год)
                '%m/%d/%Y',  # 01/09/2020 (месяц/день/год)
                '%Y-%m-%d',  # 2020-09-01
                '%d-%m-%Y',  # 01-09-2020
                '%m-%d-%Y',  # 09-01-2020
                '%d.%m.%Y',  # 01.09.2020
                '%m.%d.%Y',  # 09.01.2020
            ]

            best_format = None
            max_valid = 0

            for date_format in date_formats:
                try:
                    parsed_dates = pd.to_datetime(self.df[date_col], format=date_format, errors='coerce')
                    valid_count = parsed_dates.notna().sum()
                    print(f"🔍 Формат {date_format}: распарсено {valid_count}/{len(self.df)} дат")

                    if valid_count > max_valid:
                        max_valid = valid_count
                        best_format = date_format
                        best_parsed = parsed_dates

                except Exception as e:
                    print(f"❌ Ошибка с форматом {date_format}: {e}")
                    continue

            if best_format:
                print(f"✅ Выбран лучший формат: {best_format} ({max_valid} валидных дат)")
                self.df[date_col] = best_parsed
            else:
                # Если ни один формат не сработал, пробуем автоматическое определение
                print("🔄 Пробуем автоматическое определение дат...")
                self.df[date_col] = pd.to_datetime(self.df[date_col], errors='coerce')

            # Логируем проблемные даты
            invalid_dates = self.df[date_col].isna()
            if invalid_dates.any():
                invalid_count = invalid_dates.sum()
                print(f"⚠️  Найдено {invalid_count} некорректных дат")
                print("Примеры проблемных значений:")
                print(self.df.loc[invalid_dates, 'date_original'].head())

                # Сохраняем проблемные данные для отладки
                self.invalid_dates_data = self.df[invalid_dates][['date_original']].copy()
            else:
                self.invalid_dates_data = pd.DataFrame()

            # Удаляем строки с некорректными датами
            original_count = len(self.df)
            self.df = self.df.dropna(subset=[date_col])
            removed_count = original_count - len(self.df)
            if removed_count > 0:
                print(f"🗑️  Удалено {removed_count} строк с некорректными датами")

            # Создаем колонки для группировки по времени только для валидных дат
            valid_dates_mask = self.df[date_col].notna()
            self.df.loc[valid_dates_mask, 'year'] = self.df.loc[valid_dates_mask, date_col].dt.year
            self.df.loc[valid_dates_mask, 'month'] = self.df.loc[valid_dates_mask, date_col].dt.month
            self.df.loc[valid_dates_mask, 'year_month'] = self.df.loc[valid_dates_mask, date_col].dt.to_period('M')

            if len(self.df) > 0:
                print(
                    f"📅 Диапазон дат после очистки: {self.df[date_col].min().strftime('%d/%m/%Y')} - {self.df[date_col].max().strftime('%d/%m/%Y')}")
            else:
                print("❌ Нет валидных дат после очистки")

        # Анализ тональности текста
        if 'text' in self.column_names:
            text_col = self.column_names['text']
            self.df['sentiment'] = self.df[text_col].apply(
                lambda x: TextBlob(str(x)).sentiment.polarity if pd.notna(x) else 0
            )
            self.df['sentiment_category'] = self.df['sentiment'].apply(
                lambda x: 'Positive' if x > 0.1 else 'Negative' if x < -0.1 else 'Neutral'
            )

    def get_column(self, col_type):
        """Безопасное получение колонки"""
        return self.column_names.get(col_type, None)

    def calculate_key_metrics(self, period_data=None):
        """Расчет ключевых бизнес-метрик"""
        if period_data is None:
            period_data = self.df

        metrics = {}

        rating_col = self.get_column('rating')
        if not rating_col:
            print("❌ Колонка с рейтингами не найдена")
            return metrics

        # Основные метрики
        metrics['total_reviews'] = len(period_data)
        if len(period_data) > 0:
            metrics['avg_rating'] = period_data[rating_col].mean()
        else:
            metrics['avg_rating'] = 0

        # Распределение оценок
        if len(period_data) > 0:
            rating_counts = period_data[rating_col].value_counts().sort_index()
            metrics['rating_distribution'] = rating_counts
        else:
            metrics['rating_distribution'] = pd.Series()

        metrics['positive_reviews'] = len(period_data[period_data[rating_col] >= 4])
        metrics['negative_reviews'] = len(period_data[period_data[rating_col] <= 2])
        metrics['neutral_reviews'] = len(period_data[(period_data[rating_col] > 2) & (period_data[rating_col] < 4)])

        # NPS-like метрика
        total = metrics['total_reviews']
        if total > 0:
            metrics['nps'] = ((metrics['positive_reviews'] - metrics['negative_reviews']) / total) * 100
            metrics['csat'] = (metrics['positive_reviews'] / total) * 100
            metrics['negative_ratio'] = (metrics['negative_reviews'] / total) * 100
        else:
            metrics['nps'] = 0
            metrics['csat'] = 0
            metrics['negative_ratio'] = 0

        return metrics

    def calculate_monthly_metrics(self, start_date, end_date):
        """Расчет метрик для каждого месяца в указанном периоде"""
        date_col = self.get_column('date')
        if not date_col:
            print("❌ Колонка с датами не найдена")
            return {}

        # Проверяем, что даты корректны
        if self.df[date_col].isna().all():
            print("❌ Все даты в данных некорректны")
            return {}

        print(f"🔍 Фильтрация данных от {start_date.strftime('%d/%m/%Y')} до {end_date.strftime('%d/%m/%Y')}")

        # Фильтруем данные по периоду (включительно)
        mask = (self.df[date_col] >= start_date) & (self.df[date_col] <= end_date)
        period_data = self.df[mask].copy()

        print(f"📊 Найдено {len(period_data)} записей в выбранном периоде")

        if period_data.empty:
            print(f"⚠️  Нет данных в периоде {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}")
            return {}

        monthly_metrics = {}

        # Генерируем все месяцы в периоде
        current_date = pd.Timestamp(start_date).replace(day=1)
        end_date_ts = pd.Timestamp(end_date).replace(day=1)

        while current_date <= end_date_ts:
            year_month = current_date.strftime('%Y-%m')
            month_name = current_date.strftime('%b %Y')

            # Фильтруем данные для текущего месяца
            month_mask = (
                    (period_data[date_col].dt.year == current_date.year) &
                    (period_data[date_col].dt.month == current_date.month)
            )
            month_data = period_data[month_mask]

            if not month_data.empty:
                monthly_metrics[year_month] = {
                    'period': month_name,
                    'metrics': self.calculate_key_metrics(month_data),
                    'data': month_data
                }
            else:
                # Создаем пустые метрики для месяцев без данных
                monthly_metrics[year_month] = {
                    'period': month_name,
                    'metrics': {
                        'total_reviews': 0,
                        'avg_rating': 0,
                        'nps': 0,
                        'csat': 0,
                        'negative_ratio': 0,
                        'positive_reviews': 0,
                        'negative_reviews': 0,
                        'neutral_reviews': 0,
                    },
                    'data': pd.DataFrame()
                }

            # Переходим к следующему месяцу
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)

        print(f"📊 Рассчитаны метрики для {len(monthly_metrics)} месяцев")
        return monthly_metrics

    def create_monthly_dashboard(self, monthly_metrics):
        """Создание дашборда с месячными метриками"""
        if not monthly_metrics:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'Нет данных для выбранного периода',
                    ha='center', va='center', transform=ax.transAxes, fontsize=12)
            return fig

        fig = plt.figure(figsize=(16, 12))

        periods = list(monthly_metrics.keys())
        periods_display = [monthly_metrics[p]['period'] for p in periods]

        # Извлекаем метрики
        nps_scores = [monthly_metrics[p]['metrics'].get('nps', 0) for p in periods]
        csat_scores = [monthly_metrics[p]['metrics'].get('csat', 0) for p in periods]
        negative_ratios = [monthly_metrics[p]['metrics'].get('negative_ratio', 0) for p in periods]
        total_reviews = [monthly_metrics[p]['metrics'].get('total_reviews', 0) for p in periods]
        avg_ratings = [monthly_metrics[p]['metrics'].get('avg_rating', 0) for p in periods]

        # 1. График NPS
        ax1 = plt.subplot(3, 2, 1)
        bars = ax1.bar(periods_display, nps_scores, color=['#ff6b6b' if x < 0 else '#6bcf7f' for x in nps_scores])
        ax1.set_title('NPS по месяцам', fontweight='bold')
        ax1.set_ylabel('NPS Score')
        ax1.tick_params(axis='x', rotation=45)
        for bar, score in zip(bars, nps_scores):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width() / 2, height, f'{score:.1f}',
                     ha='center', va='bottom' if height >= 0 else 'top', fontweight='bold')

        # 2. График CSAT
        ax2 = plt.subplot(3, 2, 2)
        bars = ax2.bar(periods_display, csat_scores,
                       color=['#6bcf7f' if x > 70 else '#ffd93d' if x > 50 else '#ff6b6b' for x in csat_scores])
        ax2.set_title('CSAT по месяцам', fontweight='bold')
        ax2.set_ylabel('CSAT (%)')
        ax2.tick_params(axis='x', rotation=45)
        for bar, score in zip(bars, csat_scores):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width() / 2, height, f'{score:.1f}%',
                     ha='center', va='bottom', fontweight='bold')

        # 3. График негативных отзывов
        ax3 = plt.subplot(3, 2, 3)
        bars = ax3.bar(periods_display, negative_ratios,
                       color=['#ff6b6b' if x > 10 else '#ffd93d' if x > 5 else '#6bcf7f' for x in negative_ratios])
        ax3.set_title('Доля негативных отзывов', fontweight='bold')
        ax3.set_ylabel('Доля негативных (%)')
        ax3.tick_params(axis='x', rotation=45)
        for bar, ratio in zip(bars, negative_ratios):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width() / 2, height, f'{ratio:.1f}%',
                     ha='center', va='bottom', fontweight='bold')

        # 4. График количества отзывов
        ax4 = plt.subplot(3, 2, 4)
        bars = ax4.bar(periods_display, total_reviews, color='skyblue', alpha=0.7)
        ax4.set_title('Количество отзывов по месяцам', fontweight='bold')
        ax4.set_ylabel('Количество отзывов')
        ax4.tick_params(axis='x', rotation=45)
        for bar, count in zip(bars, total_reviews):
            height = bar.get_height()
            if count > 0:
                ax4.text(bar.get_x() + bar.get_width() / 2, height, f'{int(count)}',
                         ha='center', va='bottom', fontweight='bold')

        # 5. График средней оценки
        ax5 = plt.subplot(3, 2, 5)
        ax5.plot(periods_display, avg_ratings, marker='o', linewidth=2, color='#e377c2')
        ax5.set_title('Средняя оценка по месяцам', fontweight='bold')
        ax5.set_ylabel('Средняя оценка')
        ax5.set_ylim(0, 5.5)
        ax5.tick_params(axis='x', rotation=45)
        ax5.grid(True, alpha=0.3)
        for i, rating in enumerate(avg_ratings):
            if rating > 0:
                ax5.text(i, rating + 0.1, f'{rating:.2f}', ha='center', va='bottom', fontweight='bold')

        # 6. Сводная таблица метрик
        ax6 = plt.subplot(3, 2, 6)
        ax6.axis('off')

        table_data = []
        for period in periods:
            metrics = monthly_metrics[period]['metrics']
            table_data.append([
                monthly_metrics[period]['period'],
                metrics.get('total_reviews', 0),
                f"{metrics.get('avg_rating', 0):.2f}",
                f"{metrics.get('nps', 0):.1f}",
                f"{metrics.get('csat', 0):.1f}%",
                f"{metrics.get('negative_ratio', 0):.1f}%"
            ])

        if table_data:
            table = ax6.table(
                cellText=table_data,
                colLabels=['Период', 'Отзывов', 'Ср.оценка', 'NPS', 'CSAT', 'Негатив%'],
                cellLoc='center',
                loc='center'
            )
            table.auto_set_font_size(False)
            table.set_fontsize(9)
            table.scale(1, 1.5)

        plt.tight_layout()
        return fig

    def identify_critical_issues(self, period_data=None):
        """Выявление критических проблем из отзывов"""
        if period_data is None:
            period_data = self.df

        issues = {
            'Качество товара': 0,
            'Доставка и упаковка': 0,
            'Несоответствие описанию': 0,
            'Цена': 0,
            'Комплектация': 0,
            'Брак': 0,
            'Сервис': 0
        }

        text_col = self.get_column('text')
        rating_col = self.get_column('rating')

        if not text_col or not rating_col:
            print("❌ Колонки с текстом или рейтингами не найдены")
            return issues

        # Ключевые слова для каждой категории проблем
        keywords = {
            'Качество товара': ['качество', 'ломается', 'брак', 'некачественный', 'плохой', 'гнется', 'ломается',
                                'трескается'],
            'Доставка и упаковка': ['доставка', 'упаковка', 'пришел', 'поврежден', 'коробка', 'доставили', 'посылка'],
            'Несоответствие описанию': ['не тот', 'не соответствует', 'описание', 'отличается',
                                        'другой'],
            'Цена': ['цена', 'дорогой', 'стоимость', 'переплатил', 'дешевый', 'надорого'],
            'Комплектация': ['комплект', 'нитки', 'не хватило', 'отсутствует', 'комплектация', 'недовложение'],
            'Брак': ['брак', 'заводской', 'транспортировка', 'поврежден', 'дефект', 'скол', 'царапина'],
            'Сервис': ['продавец', 'консультация', 'обслуживание', 'поддержи', 'менеджер']
        }

        # Анализ негативных отзывов (1-3 звезды)
        negative_reviews = period_data[period_data[rating_col] <= 3]

        if negative_reviews.empty:
            # Если нет негативных, анализируем все отзывы
            negative_reviews = period_data

        for category, words in keywords.items():
            count = 0
            for word in words:
                mask = negative_reviews[text_col].astype(str).str.contains(
                    word, case=False, na=False
                )
                count += mask.sum()
            issues[category] = count

        return issues

    def create_problems_chart(self, issues):
        """График критических проблем"""
        fig, ax = plt.subplots(figsize=(10, 6))

        # Сортируем проблемы по частоте и убираем нулевые
        filtered_issues = {k: v for k, v in issues.items() if v > 0}
        if not filtered_issues:
            ax.text(0.5, 0.5, 'Не найдено критических проблем',
                    ha='center', va='center', transform=ax.transAxes)
            return fig

        sorted_issues = dict(sorted(filtered_issues.items(), key=lambda x: x[1], reverse=True))

        colors = plt.cm.Set3(np.linspace(0, 1, len(sorted_issues)))
        bars = ax.bar(sorted_issues.keys(), sorted_issues.values(), color=colors)

        # Добавляем значения на столбцы
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                    f'{int(height)}', ha='center', va='bottom')

        ax.set_title('КРИТИЧЕСКИЕ ПРОБЛЕМЫ В ОТЗЫВАХ', fontsize=14, fontweight='bold')
        ax.set_ylabel('Количество упоминаний')
        ax.tick_params(axis='x', rotation=45)
        plt.tight_layout()

        return fig


def run_streamlit_dashboard(df):
    """Запуск интерактивного дашборда Streamlit"""
    st.set_page_config(page_title="Анализ отзывов", layout="wide")

    st.title("📊 Бизнес-аналитика отзывов")
    st.markdown("---")

    try:
        # Инициализация анализатора
        analyzer = BusinessDashboard(df)

        # Боковая панель с фильтрами
        st.sidebar.header("Фильтры")

        # Фильтр по датам
        date_col = analyzer.get_column('date')
        if date_col and date_col in df.columns:
            # Получаем минимальную и максимальную даты из ВАЛИДНЫХ данных
            valid_dates = analyzer.df[analyzer.df[date_col].notna()]
            if len(valid_dates) > 0:
                min_date = valid_dates[date_col].min().date()
                max_date = valid_dates[date_col].max().date()
            else:
                # Устанавливаем диапазон по умолчанию
                min_date = date(2020, 9, 1)  # 01/09/2020
                max_date = date(2021, 10, 12)  # 12/10/2021

            st.sidebar.subheader("Выбор периода")

            # Устанавливаем период по умолчанию
            default_start = max(min_date, date(2020, 9, 1))
            default_end = min(max_date, date(2021, 10, 12))

            # Используем правильные типы дат для Streamlit
            start_date = st.sidebar.date_input(
                "Начальная дата",
                value=default_start,
                min_value=min_date,
                max_value=max_date
            )

            end_date = st.sidebar.date_input(
                "Конечная дата",
                value=default_end,
                min_value=min_date,
                max_value=max_date
            )

            # Преобразуем в datetime для внутренней обработки
            start_date_dt = pd.to_datetime(start_date)
            end_date_dt = pd.to_datetime(end_date)

            # Фильтруем данные по выбранному периоду (включительно)
            mask = (analyzer.df[date_col] >= start_date_dt) & (analyzer.df[date_col] <= end_date_dt) & (
                analyzer.df[date_col].notna())
            filtered_df = analyzer.df[mask]

            st.sidebar.write(f"**Выбран период:** {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}")
            st.sidebar.write(f"**Отзывов в периоде:** {len(filtered_df)}")

            # Сохраняем даты для использования в других методах
            start_date_final = start_date_dt
            end_date_final = end_date_dt

            # Обновляем данные в анализаторе
            analyzer.df = filtered_df
        else:
            st.sidebar.warning("Колонка с датами не найдена")
            # Устанавливаем значения по умолчанию
            start_date_final = pd.to_datetime('2020-09-01')  # 01/09/2020
            end_date_final = pd.to_datetime('2021-10-12')  # 12/10/2021

        # Фильтр по оценкам
        rating_col = analyzer.get_column('rating')
        if rating_col and rating_col in df.columns:
            min_rating, max_rating = st.sidebar.slider(
                "Диапазон оценок:",
                min_value=int(df[rating_col].min()),
                max_value=int(df[rating_col].max()),
                value=(int(df[rating_col].min()), int(df[rating_col].max()))
            )

            filtered_df = analyzer.df[(analyzer.df[rating_col] >= min_rating) &
                                      (analyzer.df[rating_col] <= max_rating)]
            analyzer.df = filtered_df

        # Вкладки для разных видов анализа
        tab1, tab2, tab3 = st.tabs(["📅 Месячный анализ", "🔍 Критические проблемы", "💬 Детальный анализ"])

        with tab1:
            st.header("📅 Анализ по месяцам")

            if date_col and date_col in df.columns:
                # Расчет месячных метрик
                monthly_metrics = analyzer.calculate_monthly_metrics(start_date_final, end_date_final)

                if monthly_metrics:
                    st.subheader("Динамика ключевых метрик по месяцам")
                    fig_monthly = analyzer.create_monthly_dashboard(monthly_metrics)
                    st.pyplot(fig_monthly)  # ✅ Исправлено

                    # Детальная таблица
                    st.subheader("Детальная статистика по месяцам")

                    table_data = []
                    for period_key, data in monthly_metrics.items():
                        metrics = data['metrics']
                        table_data.append({
                            'Период': data['period'],
                            'Отзывов': metrics.get('total_reviews', 0),
                            'Ср. оценка': f"{metrics.get('avg_rating', 0):.2f}",
                            'NPS': f"{metrics.get('nps', 0):.1f}",
                            'CSAT': f"{metrics.get('csat', 0):.1f}%",
                            'Негатив%': f"{metrics.get('negative_ratio', 0):.1f}%",
                            'Позитивные': metrics.get('positive_reviews', 0),
                            'Негативные': metrics.get('negative_reviews', 0)
                        })

                    st.dataframe(table_data, width='stretch')

                    # Анализ трендов
                    st.subheader("📊 Анализ трендов")

                    # Собираем данные для анализа
                    periods = list(monthly_metrics.keys())
                    nps_trend = [monthly_metrics[p]['metrics'].get('nps', 0) for p in periods]
                    csat_trend = [monthly_metrics[p]['metrics'].get('csat', 0) for p in periods]

                    if len(nps_trend) > 1:
                        nps_change = nps_trend[-1] - nps_trend[0]
                        csat_change = csat_trend[-1] - csat_trend[0]

                        col1, col2 = st.columns(2)

                        with col1:
                            st.metric(
                                "Изменение NPS за период",
                                f"{nps_change:+.1f}",
                                delta=f"{nps_change:+.1f}",
                                delta_color="normal"
                            )

                        with col2:
                            st.metric(
                                "Изменение CSAT за период",
                                f"{csat_change:+.1f}%",
                                delta=f"{csat_change:+.1f}%",
                                delta_color="normal"
                            )
                else:
                    st.warning("Нет данных для выбранного периода")
            else:
                st.error("Для месячного анализа необходима колонка с датами")

        with tab2:
            st.header("🔍 Критические проблемы")

            # Расчет метрик для отображения в карточках
            metrics = analyzer.calculate_key_metrics()
            issues = analyzer.identify_critical_issues()

            # Карточки с основными метриками
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Всего отзывов", metrics.get('total_reviews', 0))

            with col2:
                st.metric("Средняя оценка", f"{metrics.get('avg_rating', 0):.2f}")

            with col3:
                st.metric("NPS-показатель", f"{metrics.get('nps', 0):.1f}")

            with col4:
                st.metric("CSAT", f"{metrics.get('csat', 0):.1f}%")

            st.markdown("---")

            # График критических проблем
            st.subheader("Критические проблемы в отзывах")
            fig_problems = analyzer.create_problems_chart(issues)
            st.pyplot(fig_problems)  # ✅ Исправлено

        with tab3:
            # Детальный анализ
            st.header("💬 Детальный анализ отзывов")

            # Показ примеров проблемных отзывов
            rating_col = analyzer.get_column('rating')
            text_col = analyzer.get_column('text')

            if rating_col and text_col:
                negative_reviews = analyzer.df[analyzer.df[rating_col] <= 2]
                if not negative_reviews.empty:
                    st.write("**Примеры проблемных отзывов:**")
                    for idx, row in negative_reviews.head(5).iterrows():
                        with st.expander(f"Отзыв {row.get(analyzer.get_column('id'), 'N/A')} - {row[rating_col]}⭐"):
                            st.write(f"**Текст:** {row[text_col]}")
                            brand_col = analyzer.get_column('brand')
                            if brand_col and brand_col in row:
                                st.write(f"**Бренд:** {row[brand_col]}")
                            date_col = analyzer.get_column('date')
                            if date_col and date_col in row:
                                st.write(f"**Дата:** {row[date_col].strftime('%d/%m/%Y')}")

            # Рекомендации для бизнеса
            st.markdown("---")
            st.subheader("🚀 Рекомендации для бизнеса")

            metrics = analyzer.calculate_key_metrics()
            issues = analyzer.identify_critical_issues()

            filtered_issues = {k: v for k, v in issues.items() if v > 0}
            if filtered_issues:
                top_issues = sorted(filtered_issues.items(), key=lambda x: x[1], reverse=True)[:3]

                st.markdown("**Приоритетные действия:**")
                for issue, count in top_issues:
                    if issue == 'Качество товара':
                        st.markdown(
                            f"✅ **{issue}** ({count} упоминаний): Усилить контроль качества, пересмотреть поставщиков")
                    elif issue == 'Несоответствие описанию':
                        st.markdown(f"✅ **{issue}** ({count} упоминаний): Обновить фотографии и описания товаров")
                    elif issue == 'Брак':
                        st.markdown(f"✅ **{issue}** ({count} упоминаний): Улучшить упаковку и логистику")
                    elif issue == 'Комплектация':
                        st.markdown(f"✅ **{issue}** ({count} упоминаний): Внедрить двойную проверку комплектации")
                    elif issue == 'Цена':
                        st.markdown(f"✅ **{issue}** ({count} упоминаний): Проанализировать ценовую политику")
                    elif issue == 'Доставка и упаковка':
                        st.markdown(f"✅ **{issue}** ({count} упоминаний): Улучшить процесс доставки и упаковки")
                    elif issue == 'Сервис':
                        st.markdown(f"✅ **{issue}** ({count} упоминаний): Обучить сотрудников службы поддержки")
            else:
                st.markdown("🎉 Не найдено критических проблем для решения!")

    except Exception as e:
        st.error(f"❌ Произошла ошибка: {str(e)}")
        st.info("Проверьте наличие необходимых файлов и структуру данных")





if __name__ == "__main__":
    from loader import load_data

    df = load_data()
    run_streamlit_dashboard(df)