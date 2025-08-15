# Telegram Bot with Key Phrase Detection

A Python Telegram bot that responds to specific key phrases and sends owner notifications using python-telegram-bot 21.2.

## Features

- 🔑 **Key Phrase Detection**: Responds with a predefined message when users send a specific key phrase
- 📧 **Owner Notifications**: Sends private notifications to the bot owner when key phrases are detected
- 🎲 **Random Responses**: Replies with random messages to regular user interactions
- ⚙️ **Easy Configuration**: Simple environment variable setup
- 📝 **Comprehensive Logging**: Detailed logging for monitoring and debugging
- 🛡️ **Error Handling**: Robust error handling to keep the bot running

## Quick Setup for Replit

### 1. Create a New Replit Project

1. Go to [Replit](https://replit.com)
2. Click "Create Repl"
3. Choose "Python" as the template
4. Name your project (e.g., "telegram-bot")

### 2. Upload the Code

1. Delete the default `main.py` file in Replit
2. Copy all the files from this project into your Replit
3. Make sure you have these files:
   - `main.py`
   - `config.py` 
   - `bot_handlers.py`
   - `.env.example`
   - `README.md`

### 3. Install Dependencies

In the Replit Shell, run:
```bash
pip install python-telegram-bot==21.2 python-dotenv
