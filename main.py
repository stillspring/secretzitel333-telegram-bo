#!/usr/bin/env python3
"""
Telegram Bot Main Entry Point
A bot that responds to key phrases and sends owner notifications.
"""

import asyncio
import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from config import Config
from bot_handlers import BotHandlers

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
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
        
        # Create application
        application = Application.builder().token(config.BOT_TOKEN).build()
        logger.info("Bot application created")
        
        # Initialize handlers
        handlers = BotHandlers(config)
        
        # Add handlers to the application
        # Start command handler
        application.add_handler(CommandHandler("start", handlers.start_command))
        
        # Help command handler
        application.add_handler(CommandHandler("help", handlers.help_command))
        
        # Message handler for all text messages
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_message))
        
        # Error handler
        application.add_error_handler(handlers.error_handler)
        
        logger.info("Handlers registered successfully")
        
        # Start the bot
        logger.info("Starting bot...")
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        
        logger.info("Bot is running! Press Ctrl+C to stop.")
        
        # Keep the bot running
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("Received stop signal")
        finally:
            # Cleanup
            await application.updater.stop()
            await application.stop()
            await application.shutdown()
            logger.info("Bot stopped")
            
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
