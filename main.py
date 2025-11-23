import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters.command import Command
from aiogram import F

from database import create_table
from handlers import cmd_start, cmd_quiz, right_answer, wrong_answer, cmd_stats, cmd_leaderboard, handle_stats_button, handle_leaderboard_button

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Замените "YOUR_BOT_TOKEN" на ваш токен
API_TOKEN = 'YOUR_BOT_TOKEN'

# Объект бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Регистрируем хэндлеры
dp.message.register(cmd_start, Command("start"))
dp.message.register(cmd_quiz, F.text == "Начать игру")
dp.message.register(cmd_quiz, Command("quiz"))
dp.message.register(cmd_stats, Command("stats"))
dp.message.register(handle_stats_button, F.text == "Моя статистика")
dp.message.register(cmd_leaderboard, Command("leaderboard"))
dp.message.register(handle_leaderboard_button, F.text == "Таблица лидеров")
dp.callback_query.register(right_answer, F.data == "right_answer")
dp.callback_query.register(wrong_answer, F.data == "wrong_answer")

# Запуск процесса поллинга новых апдейтов
async def main():
    # Создаем таблицы при запуске
    await create_table()
    logging.info("Бот запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
