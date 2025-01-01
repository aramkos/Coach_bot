import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import sqlite3
import datetime
import re

# =========================
# 1. Ваш токен
# =========================
BOT_TOKEN = "7968112152:AAHuGKA9LJexcjc7EVxBXJUVrMxxuakDFgo"

DB_NAME = "health_bot.db"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())

# =========================
# 2. Работа с БД
# =========================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Таблица пользователей
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        full_name TEXT,
        total_points INTEGER DEFAULT 0,
        level TEXT DEFAULT 'Новичок'
    );
    """)

    # Таблица с данными
    c.execute("""
    CREATE TABLE IF NOT EXISTS health_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        steps INTEGER,
        sleep_hours REAL,
        weight REAL,
        workouts INTEGER,
        daily_points INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    );
    """)

    conn.commit()
    conn.close()

def get_or_create_user(user_id: int, username: str, full_name: str):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT user_id, username, full_name, total_points, level FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()

    if row is None:
        c.execute("INSERT INTO users (user_id, username, full_name, total_points, level) VALUES (?, ?, ?, ?, ?)",
                  (user_id, username, full_name, 0, 'Новичок'))
        conn.commit()
        data = {
            'user_id': user_id,
            'username': username,
            'full_name': full_name,
            'total_points': 0,
            'level': 'Новичок'
        }
    else:
        data = {
            'user_id': row[0],
            'username': row[1],
            'full_name': row[2],
            'total_points': row[3],
            'level': row[4]
        }

    conn.close()
    return data

def add_health_data(user_id: int, date_str: str, steps: int, sleep_hours: float,
                    weight: float, workouts: int, daily_points: int):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO health_data (user_id, date, steps, sleep_hours, weight, workouts, daily_points)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, date_str, steps, sleep_hours, weight, workouts, daily_points))
    conn.commit()
    conn.close()

def update_user_points(user_id: int, new_total_points: int, new_level: str):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET total_points = ?, level = ? WHERE user_id = ?",
              (new_total_points, new_level, user_id))
    conn.commit()
    conn.close()

def get_leaderboard(limit=10):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        SELECT user_id, full_name, total_points, level
        FROM users
        ORDER BY total_points DESC
        LIMIT ?
    """, (limit,))
    rows = c.fetchall()
    conn.close()

    leaders = []
    for row in rows:
        leaders.append({
            'user_id': row[0],
            'full_name': row[1],
            'total_points': row[2],
            'level': row[3]
        })
    return leaders

def get_user_stats(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT total_points, level FROM users WHERE user_id = ?", (user_id,))
    user_row = c.fetchone()
    if not user_row:
        conn.close()
        return None
    total_points, level = user_row

    c.execute("""
        SELECT
            COUNT(*),
            SUM(steps),
            AVG(sleep_hours),
            AVG(weight),
            SUM(workouts)
        FROM health_data
        WHERE user_id = ?
    """, (user_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        return None

    records_count, sum_steps, avg_sleep, avg_weight, sum_workouts = row
    if not sum_steps:
        sum_steps = 0
    if not avg_sleep:
        avg_sleep = 0
    if not avg_weight:
        avg_weight = 0
    if not sum_workouts:
        sum_workouts = 0

    return {
        "total_points": total_points,
        "level": level,
        "records_count": records_count,
        "sum_steps": int(sum_steps),
        "avg_sleep": float(avg_sleep),
        "avg_weight": float(avg_weight),
        "sum_workouts": int(sum_workouts),
    }

# =========================
# 3. Логика начисления
# =========================
def calculate_daily_points(steps, sleep_hours, workouts):
    points = (steps // 1000)
    if sleep_hours >= 7:
        points += 10
    points += 20 * workouts
    return points

def determine_level(total_points):
    if total_points < 500:
        return "Новичок"
    elif total_points < 1000:
        return "Активист"
    else:
        return "Мастер спорта"

def get_today_str():
    return datetime.date.today().isoformat()

# =========================
# 4. Обработчики
# =========================
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    user_data = get_or_create_user(
        user_id=message.from_user.id,
        username=(message.from_user.username or ""),
        full_name=(message.from_user.full_name or "").strip()
    )
    await message.answer(
        f"Привет, {user_data['full_name']}!\n"
        "Я бот для геймифицированного контроля здоровья.\n"
        "Отправьте /help, чтобы узнать мои команды."
    )

@dp.message_handler(commands=["help"])
async def cmd_help(message: types.Message):
    text = (
        "Вот что я умею:\n\n"
        "1) Принимать данные (Шаги, Сон, Вес, Тренировки).\n"
        "   Пример:\n"
        "     Шаги: 12000\n"
        "     Сон: 8\n"
        "     Вес: 75\n"
        "     Тренировки: 1\n\n"
        "2) Начислять очки и показывать рейтинг (/leaderboard).\n"
        "3) Показывать личную статистику (/mydata).\n"
        "4) Давать уровни (Новичок, Активист, Мастер спорта).\n\n"
        "Попробуйте отправить данные вручную или через Shortcut!"
    )
    await message.answer(text)

@dp.message_handler(commands=["leaderboard"])
async def cmd_leaderboard(message: types.Message):
    leaders = get_leaderboard(limit=10)
    if not leaders:
        await message.answer("Рейтинг пуст. Сначала отправьте свои данные!")
        return

    txt = "🏆 Текущий рейтинг:\n\n"
    for i, leader in enumerate(leaders, start=1):
        txt += (f"{i}. {leader['full_name']} — {leader['total_points']} очков "
                f"({leader['level']})\n")
    await message.answer(txt)

@dp.message_handler(commands=["mydata"])
async def cmd_mydata(message: types.Message):
    user_data = get_or_create_user(
        user_id=message.from_user.id,
        username=(message.from_user.username or ""),
        full_name=(message.from_user.full_name or "").strip()
    )
    stats = get_user_stats(user_data['user_id'])
    if not stats:
        await message.answer("У вас нет данных. Отправьте что-нибудь в формате 'Шаги: 10000' и т.д.")
        return

    text = (
        f"Ваша статистика:\n"
        f"• Уровень: {stats['level']}\n"
        f"• Суммарные очки: {stats['total_points']}\n"
        f"• Записей в БД: {stats['records_count']}\n"
        f"• Суммарные шаги: {stats['sum_steps']}\n"
        f"• Средний сон: {stats['avg_sleep']:.1f} ч\n"
        f"• Средний вес: {stats['avg_weight']:.1f} кг\n"
        f"• Всего тренировок: {stats['sum_workouts']}\n"
    )
    await message.answer(text)

@dp.message_handler()
async def receive_health_data(message: types.Message):
    text = message.text.lower()
    steps_match = re.search(r"шаги:\s*(\d+)", text)
    sleep_match = re.search(r"сон:\s*(\d+(\.\d+)?)", text)
    weight_match = re.search(r"вес:\s*(\d+(\.\d+)?)", text)
    workout_match = re.search(r"тренировки:\s*(\d+)", text)

    if steps_match or sleep_match or weight_match or workout_match:
        steps = int(steps_match.group(1)) if steps_match else 0
        sleep_hours = float(sleep_match.group(1)) if sleep_match else 0.0
        weight = float(weight_match.group(1)) if weight_match else 0.0
        workouts = int(workout_match.group(1)) if workout_match else 0

        daily_points = calculate_daily_points(steps, sleep_hours, workouts)

        user_data = get_or_create_user(
            user_id=message.from_user.id,
            username=(message.from_user.username or ""),
            full_name=(message.from_user.full_name or "").strip()
        )

        date_str = get_today_str()
        add_health_data(user_data['user_id'], date_str, steps, sleep_hours, weight, workouts, daily_points)

        new_total_points = user_data['total_points'] + daily_points
        new_level = determine_level(new_total_points)
        update_user_points(user_data['user_id'], new_total_points, new_level)

        await message.answer(
            f"Данные получены!\n"
            f"• Шаги: {steps}\n"
            f"• Сон: {sleep_hours:.1f} ч\n"
            f"• Вес: {weight:.1f} кг\n"
            f"• Тренировки: {workouts}\n\n"
            f"Очков сегодня: <b>{daily_points}</b>\n"
            f"Итого: <b>{new_total_points}</b>\n"
            f"Текущий уровень: <b>{new_level}</b>"
        )
    else:
        await message.answer(
            "Формат сообщения не распознан.\n"
            "Отправьте, например:\n"
            "Шаги: 10000\nСон: 8\nВес: 75\nТренировки: 1"
        )

# =========================
# 5. Запуск
# =========================
def main():
    init_db()
    executor.start_polling(dp, skip_updates=True)

if __name__ == "__main__":
    main()