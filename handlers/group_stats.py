from aiogram import types
import matplotlib.pyplot as plt
import io

@dp.message_handler(is_group_command(), commands=['group_stats'])
async def show_group_stats(message: types.Message):
    # Получаем статистику группы
    stats = await get_group_statistics()
    
    # Создаем визуализацию
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))
    
    # График общего прогресса группы
    total_weight_loss = stats['total_weight_loss']
    ax1.bar(range(len(total_weight_loss)), total_weight_loss.values())
    ax1.set_title('Общий прогресс группы')
    
    # Топ-5 участников
    top_users = stats['top_users']
    ax2.bar(range(len(top_users)), [u['progress'] for u in top_users])
    ax2.set_title('Топ-5 участников недели')
    
    # Сохраняем график
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    # Формируем текст отчета
    report = (
        "📊 Статистика группы:\n\n"
        f"👥 Всего участников: {stats['total_users']}\n"
        f"⭐️ Общий сброс веса: {stats['total_weight_loss_sum']}кг\n"
        f"💪 Тренировок за неделю: {stats['weekly_workouts']}\n\n"
        "🏆 Лидеры недели:\n"
    )
    
    for user in top_users[:5]:
        report += f"• {user['name']}: -{user['progress']}кг\n"
    
    await message.answer_photo(buf, caption=report) 