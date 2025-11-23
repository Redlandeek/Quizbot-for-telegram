import aiosqlite
from datetime import datetime

DB_NAME = 'quiz_bot.db'

async def create_table():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state 
                         (user_id INTEGER PRIMARY KEY, question_index INTEGER)''')
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_results 
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         user_id INTEGER, 
                         username TEXT, 
                         score INTEGER, 
                         total INTEGER, 
                         timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        await db.commit()

async def get_quiz_index(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id,)) as cursor:
            results = await cursor.fetchone()
            return results[0] if results else 0

async def update_quiz_index(user_id, index):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index) VALUES (?, ?)', 
                        (user_id, index))
        await db.commit()

async def save_quiz_result(user_id, username, score, total):
    async with aiosqlite.connect(DB_NAME) as db:
        # Сохраняем новый результат (не удаляем старые для истории)
        await db.execute('INSERT INTO quiz_results (user_id, username, score, total) VALUES (?, ?, ?, ?)', 
                        (user_id, username, score, total))
        await db.commit()

async def get_user_stats(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('''SELECT score, total, timestamp 
                              FROM quiz_results 
                              WHERE user_id = ? 
                              ORDER BY timestamp DESC LIMIT 1''', 
                             (user_id,)) as cursor:
            return await cursor.fetchone()

async def get_all_stats():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('''SELECT username, score, total, timestamp 
                              FROM quiz_results 
                              ORDER BY score DESC, timestamp DESC''') as cursor:
            return await cursor.fetchall()

async def get_user_best_score(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('''SELECT MAX(score), total 
                              FROM quiz_results 
                              WHERE user_id = ?''', 
                             (user_id,)) as cursor:
            return await cursor.fetchone()