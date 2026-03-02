import numpy as np
import pandas as pd
import os


def load_data():
    """Простая загрузка данных"""
    file_path = 'data/01_raw/data_for_analysis.xlsx'

    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        print(f"Данные загружены. Размер: {df.shape}")
        print(f"Колонки: {list(df.columns)}")
        return df
    else:
        print("Файл не найден. Создаем демо-данные...")
        return create_demo_data()


def create_demo_data():
    """Демо-данные если файл не найден"""
    import numpy as np
    return pd.DataFrame({
        'Текст отзыва': ['Отличный товар!', 'Нормально', 'Плохое качество'] * 10,
        'Оценка': np.random.randint(1, 6, 30),
        'Рейтинг': np.random.randint(1, 11, 30)
    })


import pandas as pd

def load_data():
    """Загрузка данных из Excel файла"""
    try:
        df = pd.read_excel('data/01_raw/data_for_analysis.xlsx')
        print("✅ Данные успешно загружены!")
        print(f"📊 Размер данных: {df.shape}")
        print(f"🔤 Колонки: {list(df.columns)}")
        print(f"📝 Первые несколько строк:")
        print(df.head(3))
        return df
    except Exception as e:
        print(f"❌ Ошибка загрузки данных: {e}")
        # Создаем демо-данные для тестирования
        print("🔄 Создаем демо-данные для тестирования...")
        return create_sample_data()

def create_sample_data():
    """Создание демо-данных если файл не найден"""
    data = {
        'ID отзыва': range(1, 101),
        'Дата': pd.date_range('2023-01-01', periods=100),
        'Номенклатура': [f'Артикул {i}' for i in range(1, 101)],
        'Количество звезд': np.random.randint(1, 6, 100),
        'Бренд': [f'Бренд {np.random.randint(1, 10)}' for _ in range(100)],
        'Текст отзыва': ['Хороший товар' if i % 2 == 0 else 'Плохой товар' for i in range(100)]
    }
    return pd.DataFrame(data)
