import sqlite3
from datetime import datetime, timedelta

def init_db():
    conn = sqlite3.connect('fitness_bot.db')
    c = conn.cursor()
    
    # Добавляем новые поля в таблицу users
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            age INTEGER,
            initial_weight REAL,
            points INTEGER DEFAULT 0,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            target_weight REAL,
            reminder_time TIME
        )
    ''')
    
    # Таблица достижений
    c.execute('''
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            achievement_type TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def save_daily_stats(user_id, weight, fat_percentage, workout_done, diet_followed):
    conn = sqlite3.connect('fitness_bot.db')
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO daily_stats 
        (user_id, weight, fat_percentage, workout_done, diet_followed, date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, weight, fat_percentage, workout_done, diet_followed, datetime.now().date()))
    
    conn.commit()
    conn.close() 