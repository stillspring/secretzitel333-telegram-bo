"""
Bot handlers module.
Contains all the message handlers and bot logic.
"""

import logging
import random
from typing import Optional
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError
from config import Config

logger = logging.getLogger(__name__)

class BotHandlers:
    """Class containing all bot message handlers."""
    
    def __init__(self, config: Config):
        """Initialize handlers with configuration."""
        self.config = config
        logger.info("Bot handlers initialized")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        try:
            user = update.effective_user
            welcome_message = (
                f"Hello {user.first_name}! 👋\n\n"
                "I'm a bot that responds to messages. Feel free to chat with me!\n\n"
                "Use /help to see available commands."
            )
            await update.message.reply_text(welcome_message)
            logger.info(f"Start command used by user {user.id} (@{user.username})")
        except Exception as e:
            logger.error(f"Error in start command: {e}")
            await self._send_error_message(update, "Sorry, something went wrong.")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command."""
        try:
            help_message = (
                "🤖 *Bot Help*\n\n"
                "Available commands:\n"
                "• /start - Start the bot\n"
                "• /help - Show this help message\n\n"
                "Just send me any message and I'll respond! 💬"
            )
            await update.message.reply_text(help_message, parse_mode='Markdown')
            logger.info(f"Help command used by user {update.effective_user.id}")
        except Exception as e:
            logger.error(f"Error in help command: {e}")
            await self._send_error_message(update, "Sorry, something went wrong.")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle all text messages."""
        try:
            if not update.message or not update.message.text:
                logger.warning("Received update without message text")
                return
            
            user = update.effective_user
            message_text = update.message.text.strip()
            
            if not message_text:
                logger.info(f"Received empty message from user {user.id}")
                return
            
            logger.info(f"Received message from {user.id} (@{user.username}): '{message_text}'")
            
            # Check if message contains key phrase
            normalized_message = self.config.normalize_text(message_text)
            key_phrase = self.config.get_effective_key_phrase()
            
            if key_phrase in normalized_message:
                await self._handle_key_phrase(update, user, message_text)
            else:
                await self._handle_regular_message(update, user, message_text)
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await self._send_error_message(update, "Sorry, I couldn't process your message.")
    
    async def _handle_key_phrase(self, update: Update, user, message_text: str) -> None:
        """Handle messages containing the key phrase."""
        try:
            # Send the predefined response to the user
            await update.message.reply_text(self.config.KEY_RESPONSE)
            logger.info(f"Key phrase detected from user {user.id}, sent key response")
            
            # Notify the owner if configured
            if self.config.OWNER_ID:
                await self._notify_owner(update.get_bot(), user, message_text)
            else:
                logger.warning("Owner notification skipped: OWNER_ID not configured")
                
        except Exception as e:
            logger.error(f"Error handling key phrase: {e}")
            raise
    
    async def _handle_regular_message(self, update: Update, user, message_text: str) -> None:
        """Handle regular messages (not containing key phrase)."""
        try:
            # Choose a random response from the list
            if self.config.OTHER_RESPONSES:
                response = random.choice(self.config.OTHER_RESPONSES)
                await update.message.reply_text(response)
                logger.info(f"Sent random response to user {user.id}")
            else:
                logger.warning("No other responses configured")
                await update.message.reply_text("Thanks for your message!")
                
        except Exception as e:
            logger.error(f"Error handling regular message: {e}")
            raise
    
    async def _notify_owner(self, bot, user, message_text: str) -> None:
        """Send notification to the bot owner."""
        try:
            username = user.username if user.username else "No username"
            user_full_name = f"{user.first_name} {user.last_name or ''}".strip()
            
            notification_message = (
                "🔔 *Key Phrase Detected!*\n\n"
                f"👤 *User:* {user_full_name}\n"
                f"🆔 *User ID:* `{user.id}`\n"
                f"📝 *Username:* @{username}\n"
                f"💬 *Message:* {message_text}\n\n"
                f"🕐 *Time:* {update.message.date.strftime('%Y-%m-%d %H:%M:%S UTC') if hasattr(update, 'message') and update.message else 'Unknown'}"
            )
            
            await bot.send_message(
                chat_id=self.config.OWNER_ID,
                text=notification_message,
                parse_mode='Markdown'
            )
            logger.info(f"Owner notification sent for user {user.id}")
            
        except TelegramError as e:
            logger.error(f"Failed to send owner notification: {e}")
            # Don't raise here as the main message was already sent
        except Exception as e:
            logger.error(f"Unexpected error sending owner notification: {e}")
    
    async def _send_error_message(self, update: Update, message: str) -> None:
        """Send an error message to the user."""
        try:
            if update.message:
                await update.message.reply_text(message)
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle errors that occur during update processing."""
        logger.error(f"Exception while handling an update: {context.error}")
        
        # Try to send a message to the user if possible
        if isinstance(update, Update) and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "Sorry, something went wrong. Please try again later."
                )
            except Exception as e:
                logger.error(f"Failed to send error message to user: {e}")
