from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

class DailySurveyStates(StatesGroup):
    waiting_for_weight = State()
    waiting_for_fat = State()
    waiting_for_workout = State()
    waiting_for_diet = State()

async def start_daily_survey(message: types.Message):
    await message.answer(
        "Давайте заполним данные за сегодня! 📝\n"
        "Введите ваш текущий вес (в кг):"
    )
    await DailySurveyStates.waiting_for_weight.set()

async def process_weight(message: types.Message, state: FSMContext):
    try:
        weight = float(message.text)
        async with state.proxy() as data:
            data['weight'] = weight
        
        await message.answer("Введите процент жира (если измеряли):\nЕсли не измеряли, напишите 'нет'")
        await DailySurveyStates.waiting_for_fat.set()
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число!") 