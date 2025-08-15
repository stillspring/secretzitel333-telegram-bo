#!/usr/bin/env python3
"""
Telegram Bot Main Entry Point
A bot that responds to key phrases and sends owner notifications.
"""

import logging
import telebot
from config import Config
from bot_handlers import BotHandlers

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Main function to initialize and run the bot."""
    try:
        # Load configuration
        config = Config()
        logger.info("Configuration loaded successfully")
        
        # Validate required configuration
        if not config.BOT_TOKEN:
            logger.error("BOT_TOKEN is required but not found in environment variables")
            return
        
        if not config.OWNER_ID:
            logger.error("OWNER_ID is required but not found in environment variables")
            return
        
        # Create bot instance
        bot = telebot.TeleBot(config.BOT_TOKEN)
        logger.info("Bot instance created")
        
        # Initialize handlers
        handlers = BotHandlers(config, bot)
        
        # Register message handlers
        @bot.message_handler(commands=['start'])
        def start_command(message):
            handlers.start_command(message)
        
        @bot.message_handler(commands=['help'])
        def help_command(message):
            handlers.help_command(message)
        
        @bot.message_handler(func=lambda message: True)
        def handle_all_messages(message):
            handlers.handle_message(message)
        
        logger.info("Handlers registered successfully")
        
        # Start the bot
        logger.info("Starting bot...")
        logger.info("Bot is running! Press Ctrl+C to stop.")
        bot.polling(none_stop=True)
            
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
