from aiogram import types
from database import update_user_points, get_user_achievements

class RewardSystem:
    ACHIEVEMENTS = {
        'weight_milestone': {
            'points': 100,
            'title': '🎯 Достигнута цель по весу!',
            'description': 'Вы достигли очередной цели по снижению веса'
        },
        'workout_streak': {
            'points': 50,
            'title': '🔥 Серия тренировок!',
            'description': 'Вы тренировались 7 дней подряд'
        },
        'diet_master': {
            'points': 75,
            'title': '🥗 Мастер питания!',
            'description': 'Следование плану питания 14 дней подряд'
        },
        'survey_champion': {
            'points': 25,
            'title': '📊 Чемпион статистики!',
            'description': '30 дней регулярного заполнения данных'
        }
    }
    
    @staticmethod
    async def check_and_award_achievements(user_id: int, stats: dict):
        new_achievements = []
        
        # Проверяем различные достижения
        if stats['weight_loss'] >= stats['weight_goal'] * 0.1:  # 10% от цели
            new_achievements.append('weight_milestone')
            
        if stats['workout_streak'] >= 7:
            new_achievements.append('workout_streak')
            
        if stats['diet_streak'] >= 14:
            new_achievements.append('diet_master')
            
        if stats['survey_streak'] >= 30:
            new_achievements.append('survey_champion')
        
        # Начисляем очки и сохраняем достижения
        for achievement in new_achievements:
            await update_user_points(user_id, RewardSystem.ACHIEVEMENTS[achievement]['points'])
            
        return new_achievements

async def show_achievements(message: types.Message):
    user_id = message.from_user.id
    achievements = await get_user_achievements(user_id)
    
    response = "🏆 Ваши достижения:\n\n"
    for achievement in achievements:
        ach_info = RewardSystem.ACHIEVEMENTS[achievement['type']]
        response += f"{ach_info['title']}\n"
        response += f"└ {ach_info['description']}\n"
        response += f"└ +{ach_info['points']} очков\n\n"
    
    await message.answer(response) 