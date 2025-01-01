from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
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

# Обработчик команды /survey
@dp.message_handler(commands=["survey"], chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def survey_command(message: types.Message):
    if message.chat.id != GROUP_ID:
        await message.reply("Эта команда доступна только в указанной группе.")
        return

    user_id = message.from_user.id
    user_data[user_id] = {"weight": None, "fat": None}

    # Отправляем сообщение с кнопками для начала ввода данных
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Начать ввод данных", callback_data=f"start_survey:{user_id}"))
    await message.reply(
        f"{message.from_user.first_name}, нажмите на кнопку ниже, чтобы начать ввод данных.",
        reply_markup=keyboard
    )

# Обработчик нажатия на кнопку "Начать ввод данных"
@dp.callback_query_handler(lambda call: call.data.startswith("start_survey"))
async def start_survey(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[1])

    # Проверяем, что пользователь совпадает
    if callback.from_user.id != user_id:
        await callback.answer("Вы не можете начать этот опрос.", show_alert=True)
        return

    # Отправляем сообщение для ввода веса
    await bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text="Введите ваш вес (в кг):"
    )

    # Сохраняем текущий этап опроса
    user_data[user_id]["stage"] = "weight"

# Обработчик ввода данных
@dp.message_handler()
async def handle_input(message: types.Message):
    user_id = message.from_user.id

    # Проверяем, что пользователь проходит опрос
    if user_id not in user_data or "stage" not in user_data[user_id]:
        return

    stage = user_data[user_id]["stage"]

    if stage == "weight":
        try:
            weight = float(message.text)
            user_data[user_id]["weight"] = weight
            user_data[user_id]["stage"] = "fat"

            # Отправляем сообщение для ввода процента жира
            await message.reply("Введите процент жира (%):")
        except ValueError:
            await message.reply("Пожалуйста, введите корректный вес (число).")

    elif stage == "fat":
        try:
            fat = float(message.text)
            user_data[user_id]["fat"] = fat
            user_data[user_id]["stage"] = "completed"

            # Итоговое сообщение
            await message.reply(
                f"Ваши данные сохранены!\nВес: {user_data[user_id]['weight']} кг\nПроцент жира: {user_data[user_id]['fat']}%"
            )
        except ValueError:
            await message.reply("Пожалуйста, введите корректный процент жира (число).")

# Команда /stats для просмотра сохранённых данных
@dp.message_handler(commands=["stats"], chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def stats_command(message: types.Message):
    data = user_data.get(message.from_user.id)
    if data and data.get("stage") == "completed":
        await message.reply(
            f"Ваши данные:\nВес: {data['weight']} кг\nПроцент жира: {data['fat']}%"
        )
    else:
        await message.reply("Ваших данных пока нет. Напишите /survey, чтобы внести их.")

# Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)