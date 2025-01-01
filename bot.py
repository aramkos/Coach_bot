from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from dotenv import load_dotenv
import os

# Загрузка переменных окружения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Временное хранилище данных (в памяти)
user_data = {}

# Обработчик команды /start (только в личных сообщениях)
@dp.message_handler(commands=["start"], chat_type=types.ChatType.PRIVATE)
async def start_command(message: types.Message):
    await message.reply("Привет! Я твой фитнес-бот. Напиши /survey в группе, чтобы внести данные.")

# Обработчик команды /survey (только в группе)
@dp.message_handler(commands=["survey"], chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def survey_command(message: types.Message):
    if message.chat.id != GROUP_ID:
        await message.reply("Эта команда доступна только в указанной группе.")
        return

    user_id = message.from_user.id
    user_data[user_id] = {}
    await message.reply(f"{message.from_user.first_name}, введите ваш вес (в кг):")
    dp.register_message_handler(weight_handler, user_id=user_id)

# Обработчик ввода веса
async def weight_handler(message: types.Message):
    try:
        weight = float(message.text)
        user_data[message.from_user.id]["weight"] = weight
        await message.reply("Введите процент жира (%):")
        dp.register_message_handler(fat_handler, user_id=message.from_user.id)
    except ValueError:
        await message.reply("Пожалуйста, введите корректный вес (число).")

# Обработчик ввода процента жира
async def fat_handler(message: types.Message):
    try:
        fat = float(message.text)
        user_data[message.from_user.id]["fat"] = fat
        await message.reply("Данные сохранены! Напишите /stats, чтобы посмотреть их.")
    except ValueError:
        await message.reply("Пожалуйста, введите корректный процент жира (число).")

# Обработчик команды /stats (только в группе)
@dp.message_handler(commands=["stats"], chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def stats_command(message: types.Message):
    if message.chat.id != GROUP_ID:
        await message.reply("Эта команда доступна только в указанной группе.")
        return

    data = user_data.get(message.from_user.id)
    if data:
        await message.reply(
            f"{message.from_user.first_name}, ваши данные:\n"
            f"Вес: {data['weight']} кг\nПроцент жира: {data['fat']}%"
        )
    else:
        await message.reply("Ваших данных пока нет. Напишите /survey, чтобы внести их.")

# Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)