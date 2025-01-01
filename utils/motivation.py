def generate_motivation_message(user_stats: dict, group_stats: dict) -> str:
    """Генерирует мотивационное сообщение на основе статистики"""
    
    message = "📊 Ваш прогресс:\n\n"
    
    # Анализ снижения веса
    weight_diff = user_stats['weight_loss_percentage'] - group_stats['avg_weight_loss']
    if weight_diff > 0:
        message += f"🌟 Вы снижаете вес на {weight_diff:.1f}% лучше среднего по группе!\n"
    else:
        message += "💪 Продолжайте работать над своей целью!\n"
    
    # Анализ активности
    if user_stats['workout_rate'] > group_stats['avg_workout_rate']:
        message += "🏃‍♂️ Вы одни из самых активных участников группы!\n"
    
    # Достижения
    if user_stats['current_streak'] > 0:
        message += f"🔥 Текущая серия: {user_stats['current_streak']} дней\n"
    
    # Мотивационная фраза
    phrases = [
        "Каждый день приближает вас к цели! 🎯",
        "Вы на правильном пути! 🌟",
        "Продолжайте в том же духе! 💪",
        "Ваше упорство вдохновляет других! 🌈"
    ]
    message += f"\n{random.choice(phrases)}"
    
    return message 