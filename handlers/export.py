import pandas as pd
from io import BytesIO
from aiogram import types
from database import get_user_stats, get_group_stats, get_user_achievements

async def export_personal_data(message: types.Message):
    user_id = message.from_user.id
    user_stats = get_user_stats(user_id)
    
    # Создаем Excel файл
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    
    # Лист с личной статистикой
    df_personal = pd.DataFrame(user_stats)
    df_personal.to_excel(writer, sheet_name='Личная статистика')
    
    # Лист с достижениями
    df_achievements = pd.DataFrame(get_user_achievements(user_id))
    df_achievements.to_excel(writer, sheet_name='Достижения')
    
    # Добавляем графики
    workbook = writer.book
    worksheet = writer.sheets['Личная статистика']
    
    # График прогресса веса
    chart = workbook.add_chart({'type': 'line'})
    chart.add_series({
        'name': 'Вес',
        'categories': '=Личная статистика!$B$2:$B$32',
        'values': '=Личная статистика!$C$2:$C$32'
    })
    worksheet.insert_chart('H2', chart)
    
    writer.save()
    output.seek(0)
    
    await message.answer_document(
        ('statistics.xlsx', output),
        caption="📊 Ваша персональная статистика"
    ) 