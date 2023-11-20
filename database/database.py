import sqlite3
from config import DB_NAME

# Connect to SQLite database (it will be created if it doesn't exist)

async def db_start():
    global db, cur

    db = sqlite3.connect(DB_NAME)
    cur = db.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS competition (user_id INTEGER PRIMARY KEY,
              nickname TEXT,
              submissions INTEGER NOT NULL,
              best_score REAL)
             ''')

    db.commit()