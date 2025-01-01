from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
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

# Обработчик команды /survey (начало опроса в группе)
@dp.message_handler(commands=["survey"], chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def survey_command(message: types.Message):
    if message.chat.id != GROUP_ID:
        await message.reply("Эта команда доступна только в указанной группе.")
        return

    # Создание инлайн-кнопки
    keyboard = InlineKeyboardMarkup()
    button = InlineKeyboardButton(
        text="Продолжить в личных сообщениях",
        url=f"tg://user?id={message.from_user.id}"
    )
    keyboard.add(button)

    await message.reply(
        f"{message.from_user.first_name}, нажмите на кнопку ниже, чтобы продолжить опрос в личных сообщениях.",
        reply_markup=keyboard
    )

# Обработчик опроса в личных сообщениях
@dp.message_handler(chat_type=types.ChatType.PRIVATE)
async def private_survey(message: types.Message):
    user_id = message.from_user.id

    # Если пользователь начинает опрос
    if user_id not in user_data:
        user_data[user_id] = {"stage": "weight"}
        await message.reply("Введите ваш вес (в кг):")
        return

    # Проверка текущей стадии
    stage = user_data[user_id]["stage"]

    if stage == "weight":
        try:
            weight = float(message.text)
            user_data[user_id]["weight"] = weight
            user_data[user_id]["stage"] = "fat"
            await message.reply("Введите процент жира (%):")
        except ValueError:
            await message.reply("Пожалуйста, введите корректный вес (число).")

    elif stage == "fat":
        try:
            fat = float(message.text)
            user_data[user_id]["fat"] = fat
            user_data[user_id]["stage"] = "completed"
            await message.reply("Данные сохранены! Спасибо за участие.")
        except ValueError:
            await message.reply("Пожалуйста, введите корректный процент жира (число).")

# Обработчик команды /stats (вывод данных)
@dp.message_handler(commands=["stats"], chat_type=types.ChatType.PRIVATE)
async def stats_command(message: types.Message):
    data = user_data.get(message.from_user.id)
    if data and data.get("stage") == "completed":
        await message.reply(
            f"Ваши данные:\nВес: {data['weight']} кг\nПроцент жира: {data['fat']}%"
        )
    else:
        await message.reply("Ваших данных пока нет. Напишите /survey в группе, чтобы внести их.")

# Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)