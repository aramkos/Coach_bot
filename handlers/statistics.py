from aiogram import types
import matplotlib.pyplot as plt
import io
from database import get_user_stats

async def show_personal_stats(message: types.Message):
    user_id = message.from_user.id
    stats = get_user_stats(user_id)
    
    # Создаем график прогресса
    plt.figure(figsize=(10, 6))
    plt.plot([s['date'] for s in stats], [s['weight'] for s in stats], 'b-')
    plt.title('Динамика веса')
    plt.xlabel('Дата')
    plt.ylabel('Вес (кг)')
    
    # Сохраняем график в байтовый поток
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    await message.answer_photo(
        buf,
        caption="Ваш прогресс за последний месяц 📊"
    ) 