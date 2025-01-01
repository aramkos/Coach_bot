from aiogram import Bot
import asyncio
from datetime import datetime, time
from database import get_active_users

async def send_daily_reminder(bot: Bot):
    while True:
        now = datetime.now().time()
        if now.hour == 20 and now.minute == 0:  # Отправляем напоминание в 20:00
            users = get_active_users()
            for user in users:
                await bot.send_message(
                    user['user_id'],
                    "Не забудьте заполнить данные за сегодня! 🎯\n"
                    "Используйте команду /survey для заполнения."
                )
        await asyncio.sleep(60)  # Проверяем каждую минуту 