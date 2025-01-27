# competition_bot
Bot for data science competitions in telegram

## Dependencies:
```
aiogram==2.25.1
pandas==2.1.3
lifelines==0.27.8
```

## Important notes
* Do not forget to create and enter your `TELEGRAM_API_TOKEN` to `.env` file.
* If you need to modify **target metric** somehow, work with `utils.utils` file.
* Note, the bot works with `test_answer.csv` file to compare with. Ensure files are in the same format.

To run use the following command:
```
python main.py
```

## bot commands
`/start` - starts bot. If it is the first bot usage, it will propose to enter the nickname. Next, the bot will offer to send a `.csv` file with answer. If the file in the appropriate format, bot will calcuate a test score and report it. Otherwise it returns message with error.

`/leaderboard` - bot returns a table with leaderboard, where names and test scores only are presetned.

