from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

class DailyReport(StatesGroup):
    waiting_for_weight = State()
    waiting_for_photo = State()
    waiting_for_comment = State()

@dp.message_handler(is_group_command(), commands=['report'])
async def start_daily_report(message: types.Message):
    user_mention = message.from_user.get_mention()
    await message.reply(
        f"{user_mention}, давайте заполним отчет за сегодня!\n"
        "Укажите свой текущий вес:"
    )
    await DailyReport.waiting_for_weight.set()

@dp.message_handler(state=DailyReport.waiting_for_weight)
async def process_weight(message: types.Message, state: FSMContext):
    try:
        weight = float(message.text)
        await state.update_data(weight=weight)
        
        await message.reply(
            "Отлично! Теперь отправьте фото вашего прогресса (если есть)\n"
            "Или напишите 'пропустить'"
        )
        await DailyReport.waiting_for_photo.set()
    except ValueError:
        await message.reply("Пожалуйста, введите корректное число!") 