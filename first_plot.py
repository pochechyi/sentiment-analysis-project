# first_plot.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

print("🎨 Начинаем строить графики...")

# Загружаем данные
file_path = "data/01_raw/data_for_analysis.xlsx"
df = pd.read_excel(file_path)

print("📋 Колонки в данных:")
for i, col in enumerate(df.columns, 1):
    print(f"   {i}. {col}")

# 1. ГРАФИК: Распределение оценок (гистограмма)
plt.figure(figsize=(10, 6))

# Ищем колонку с оценками
rating_column = None
for col in df.columns:
    if 'оцен' in col.lower() or 'рейтинг' in col.lower() or 'rating' in col.lower():
        rating_column = col
        break

if rating_column:
    # Гистограмма оценок
    plt.subplot(1, 2, 1)  # 1 строка, 2 колонки, 1й график
    df[rating_column].hist(bins=5, alpha=0.7, edgecolor='black')
    plt.title('Распределение оценок')
    plt.xlabel('Оценка')
    plt.ylabel('Количество отзывов')

    # Круговая диаграмма
    plt.subplot(1, 2, 2)  # 1 строка, 2 колонки, 2й график
    rating_counts = df[rating_column].value_counts()
    plt.pie(rating_counts.values, labels=rating_counts.index, autopct='%1.1f%%')
    plt.title('Процентное соотношение оценок')

    plt.tight_layout()
    plt.show()

    print(f"✅ Построены графики для колонки: {rating_column}")
else:
    print("❌ Не найдена колонка с оценками")

print("📊 Статистика по числовым колонкам:")
print(df.describe())