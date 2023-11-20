import os
from dotenv import load_dotenv
from aiogram import types
import aiogram.utils.markdown as md

#load variables
load_dotenv()

#tokens
BOT_TOKEN = os.environ.get("TELEGRAM_API_TOKEN")

#db
DB_NAME = 'database/competition.db'

#other params
MAX_SUBMITS = 100

#texts
HELP_TEXT = md.text(
                md.text("Bot description..."),
                md.text("Useful commands:"),
                md.text("/help - returns help"),
                md.text("/start - start bot."),
                sep='\n',
            )
