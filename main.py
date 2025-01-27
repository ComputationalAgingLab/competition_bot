import aiogram
import asyncio
import pandas as pd
import sqlite3
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ContentType
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import *
from database.database import db_start
from utils.utils import calculate_metric

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

# Initialize answer
test_answer = pd.read_csv('competition/test_answer.csv', index_col=0)

# temporal states
class Form(StatesGroup):
    nickname = State()

async def on_startup(_):
    await db_start()

@dp.message_handler(CommandStart())
async def cmd_start(message: types.Message):
    """
    Entry point
    """
    # Set state
    user_id = message.from_user.id
    # response = get_time_zone(message.from_user.id)
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    cur.execute("SELECT nickname FROM competition WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    if row:
        _ = row[0]
    else:
        cur.execute("INSERT INTO competition (user_id, nickname, submissions, best_score) VALUES (?, ?, ?, ?)", (user_id, '', 0, 0.0))        

    conn.commit()
    conn.close()

    if row is None:
        await Form.nickname.set()
        await bot.send_message(user_id, "Choose your nickname:", )
    else:
        await bot.send_message(user_id, "Send .csv file with your solution.")

@dp.message_handler(state=Form.nickname)
async def process_task_name(message: types.Message, state: FSMContext):
    """
    Process nickname name
    """
    user_id = message.chat.id
    nickname = message.text
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("UPDATE competition SET nickname = ? WHERE user_id = ?", (nickname, user_id))
    conn.commit()
    conn.close()
    
    await bot.send_message(user_id, "Send .csv file with your solution.")
    await state.finish()


# Handler for file reception
@dp.message_handler(content_types=[ContentType.DOCUMENT])
async def handle_document(message: types.Message):
    user_id = message.from_user.id

    # Connect to the database
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # check the number of submissions
    cur.execute("SELECT submissions FROM competition WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    if row:
        nsub = row[0]
    else:
        nsub = 0
        cur.execute("INSERT INTO competition (user_id, submissions, best_score) VALUES (?, ?, ?)", (user_id, 0, 0.0))
        
    if nsub < MAX_SUBMITS:
        # Save the file locally
        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        await bot.download_file(file_path, f'submissions/{user_id}_answer.csv')

        try:
            # Calculate metric
            predicted_hazards = pd.read_csv(f'submissions/{user_id}_answer.csv', index_col=0)
            score = calculate_metric(test_answer, predicted_hazards)
            score = round(score, 5)
            nsub += 1

            # Update database
            # Check if user already exists
            cur.execute("SELECT best_score FROM competition WHERE user_id = ?", (user_id,))
            row = cur.fetchone()
            if score > row[0]:  # Assuming higher score is better;
                cur.execute("UPDATE competition SET submissions = submissions + 1, best_score = ? WHERE user_id = ?", (score, user_id))
            else:
                cur.execute("UPDATE competition SET submissions = ? WHERE user_id = ?", (nsub, user_id))
            # Send back the score
            await message.reply(f"Your score is: {score}\n{MAX_SUBMITS - nsub} submissions left.")
        except:
            await message.reply(f"Wrong file format!")

        conn.commit()
        conn.close()

    else:
        await message.reply(f"You exceed the limit of submissions.")

# Handler for leaderboard
@dp.message_handler(commands='leaderboard')
async def send_leaderboard(message: types.Message):
    leaderboard = "Leaderboard:\n\n"
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT nickname, best_score FROM competition ORDER BY best_score DESC")
    for row in cur:
        leaderboard += f"{row[0]}: Score: {row[1]}\n"
    conn.close()

    await message.answer(leaderboard)

# Run the bot
if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(dp.start_polling())
    executor.start_polling(dp, 
                    skip_updates=True,
                    on_startup=on_startup,
                    ) 
