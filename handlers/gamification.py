from aiogram import types
from database import update_user_points, get_leaderboard

async def award_points(user_id: int, activity: str):
    points = {
        'survey_complete': 10,
        'workout_done': 15,
        'diet_followed': 10,
        'weight_goal_reached': 50
    }
    
    if activity in points:
        await update_user_points(user_id, points[activity])

async def show_leaderboard(message: types.Message):
    leaderboard = await get_leaderboard()
    response = "🏆 Таблица лидеров:\n\n"
    
    for i, user in enumerate(leaderboard, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "▫️"
        response += f"{medal} {i}. {user['name']} - {user['points']} очков\n"
    
    await message.answer(response) 