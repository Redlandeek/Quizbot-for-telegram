from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from datetime import datetime

from database import get_quiz_index, update_quiz_index, save_quiz_result, get_user_stats, get_all_stats, get_user_best_score
from quiz_data import quiz_data
from keyboards import generate_options_keyboard

user_scores = {}

async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    builder.add(types.KeyboardButton(text="Моя статистика"))
    builder.add(types.KeyboardButton(text="Таблица лидеров"))
    await message.answer(
        "Добро пожаловать в квиз по программированию! \n\n"
        "Выберите действие:",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )

async def cmd_quiz(message: types.Message):
    user_id = message.from_user.id
    user_scores[user_id] = 0  # Сбрасываем счетчик правильных ответов
    await message.answer("Давайте начнем квиз!")
    await new_quiz(message)

async def new_quiz(message):
    user_id = message.from_user.id
    await update_quiz_index(user_id, 0)
    await get_question(message, user_id)

async def get_question(message, user_id):
    current_question_index = await get_quiz_index(user_id)
    
    if current_question_index < len(quiz_data):
        question_data = quiz_data[current_question_index]
        correct_index = question_data['correct_option']
        opts = question_data['options']
        kb = generate_options_keyboard(opts, opts[correct_index])
        await message.answer(f"Вопрос {current_question_index + 1}/{len(quiz_data)}:\n\n{question_data['question']}", reply_markup=kb)
    else:
        # Квиз завершен
        score = user_scores.get(user_id, 0)
        total = len(quiz_data)
        
        # Сохраняем результат
        username = message.from_user.username or message.from_user.first_name
        if not username:
            username = f"User_{user_id}"
            
        await save_quiz_result(user_id, username, score, total)
        
        # Удаляем счетчик пользователя
        if user_id in user_scores:
            del user_scores[user_id]
            
        await message.answer(
            f" Квиз завершен!\n"
            f"Ваш результат: {score}/{total} правильных ответов\n"
            f"Процент правильных ответов: {round(score/total*100, 1)}%"
        )

async def right_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    
    # Увеличиваем счетчик правильных ответов
    user_scores[user_id] = user_scores.get(user_id, 0) + 1
    
    # Удаляем кнопки
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    await callback.message.answer("Верно!")
    
    current_question_index = await get_quiz_index(user_id)
    current_question_index += 1
    await update_quiz_index(user_id, current_question_index)

    await get_question(callback.message, user_id)

async def wrong_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    
    # Удаляем кнопки
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    current_question_index = await get_quiz_index(user_id)
    correct_option = quiz_data[current_question_index]['correct_option']
    correct_answer = quiz_data[current_question_index]['options'][correct_option]

    await callback.message.answer(f" Неправильно. Правильный ответ: {correct_answer}")
    
    current_question_index += 1
    await update_quiz_index(user_id, current_question_index)

    await get_question(callback.message, user_id)

async def cmd_stats(message: types.Message):
    user_id = message.from_user.id
    stats = await get_user_stats(user_id)
    
    if stats:
        score, total, timestamp = stats
        # Форматируем дату
        if isinstance(timestamp, str):
            formatted_time = timestamp
        else:
            formatted_time = timestamp.split('.')[0] if timestamp else "Неизвестно"
            
        await message.answer(
            f"📊 Ваша статистика:\n"
            f"Последний результат: {score}/{total}\n"
            f"Процент правильных: {round(score/total*100, 1)}%\n"
            f"Дата: {formatted_time}"
        )
    else:
        await message.answer("У вас еще нет результатов квиза. Начните игру с помощью /quiz")

async def cmd_leaderboard(message: types.Message):
    try:
        stats = await get_all_stats()
        
        if not stats:
            await message.answer("Пока нет результатов игроков. Будьте первым!")
            return
        
        leaderboard_text = "Таблица лидеров:\n\n"
        
        for i, (username, score, total, timestamp) in enumerate(stats[:10], 1):
            percentage = round(score/total*100, 1)
            # Обрезаем длинные имена
            display_name = username if len(username) <= 15 else username[:15] + "..."
            leaderboard_text += f"{i}. {display_name}: {score}/{total} ({percentage}%)\n"
        
        await message.answer(leaderboard_text)
    except Exception as e:
        await message.answer(f" Ошибка при загрузке таблицы лидеров: {str(e)}")

# Добавляем обработчики для кнопок
async def handle_stats_button(message: types.Message):
    await cmd_stats(message)

async def handle_leaderboard_button(message: types.Message):
    await cmd_leaderboard(message)