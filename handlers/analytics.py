from aiogram import types
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from database import get_group_stats, get_user_stats
import numpy as np

async def show_comparative_analysis(message: types.Message):
    user_id = message.from_user.id
    
    # Получаем статистику пользователя и группы
    user_stats = get_user_stats(user_id)
    group_stats = get_group_stats()
    
    # Создаем сравнительный анализ
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # График прогресса снижения веса
    sns.lineplot(data=group_stats, x='date', y='weight_loss_percentage', 
                label='Среднее по группе', ax=ax1, color='blue', alpha=0.3)
    sns.lineplot(data=user_stats, x='date', y='weight_loss_percentage',
                label='Ваш прогресс', ax=ax1, color='red')
    ax1.set_title('Процент снижения веса')
    
    # График активности
    activity_data = pd.DataFrame({
        'Показатель': ['Тренировки', 'Правильное питание', 'Заполнение данных'],
        'Ваш показатель': [user_stats['workout_rate'], user_stats['diet_rate'], user_stats['survey_rate']],
        'Средний показатель': [group_stats['avg_workout_rate'], group_stats['avg_diet_rate'], group_stats['avg_survey_rate']]
    })
    
    activity_data.plot(kind='bar', ax=ax2)
    ax2.set_title('Сравнение активности (в %)')
    
    # Сохраняем график
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    
    # Формируем мотивационное сообщение
    motivation_text = generate_motivation_message(user_stats, group_stats)
    
    await message.answer_photo(buf, caption=motivation_text) 