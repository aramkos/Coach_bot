from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TOKEN, GROUP_ID
import logging

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Проверка, что команда пришла из нужной группы
def is_group_command():
    async def check(message: types.Message):
        return message.chat.id == GROUP_ID
    return check

@dp.message_handler(is_group_command(), commands=['start'])
async def cmd_start(message: types.Message):
    await message.reply(
        "Привет! Я бот для отслеживания фитнес-прогресса группы! 💪\n"
        "Доступные команды:\n"
        "/register - Зарегистрироваться в системе\n"
        "/stats - Показать свою статистику\n"
        "/group_stats - Статистика группы\n"
        "/report - Отчет за день\n"
        "/leaderboard - Таблица лидеров"
    )

# Обработка регистрации через реплай
@dp.message_handler(is_group_command(), commands=['register'])
async def register_user(message: types.Message):
    user = message.from_user
    await message.reply(
        f"@{user.username}, давайте начнем регистрацию!\n"
        "Укажите свой текущий вес (например: 70.5)"
    ) 