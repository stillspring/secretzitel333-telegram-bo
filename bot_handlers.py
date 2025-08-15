"""
Bot handlers module.
Contains all the message handlers and bot logic.
"""

import logging
import random
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

class BotHandlers:
    """Class containing all bot message handlers."""
    
    def __init__(self, config: Config, bot):
        """Initialize handlers with configuration and bot instance."""
        self.config = config
        self.bot = bot
        logger.info("Bot handlers initialized")
    
    def start_command(self, message):
        """Handle /start command."""
        try:
            user = message.from_user
            welcome_message = (
                f"Hello {user.first_name}!\n\n"
                "I'm a bot that responds to messages. Feel free to chat with me!\n\n"
                "Use /help to see available commands."
            )
            self.bot.reply_to(message, welcome_message)
            logger.info(f"Start command used by user {user.id} (@{user.username})")
        except Exception as e:
            logger.error(f"Error in start command: {e}")
            self._send_error_message(message, "Sorry, something went wrong.")
    
    def help_command(self, message):
        """Handle /help command."""
        try:
            help_message = (
                "🤖 *Bot Help*\n\n"
                "Available commands:\n"
                "• /start - Start the bot\n"
                "• /help - Show this help message\n\n"
                "Just send me any message and I'll respond! 💬"
            )
            self.bot.reply_to(message, help_message, parse_mode='Markdown')
            logger.info(f"Help command used by user {message.from_user.id}")
        except Exception as e:
            logger.error(f"Error in help command: {e}")
            self._send_error_message(message, "Sorry, something went wrong.")
    
    def handle_message(self, message):
        """Handle all text messages."""
        try:
            if not message.text:
                logger.warning("Received message without text")
                return
            
            user = message.from_user
            message_text = message.text.strip()
            
            if not message_text:
                logger.info(f"Received empty message from user {user.id}")
                return
            
            logger.info(f"Received message from {user.id} (@{user.username}): '{message_text}'")
            
            # Check if message contains key phrase
            normalized_message = self.config.normalize_text(message_text)
            key_phrase = self.config.get_effective_key_phrase()
            
            if key_phrase in normalized_message:
                self._handle_key_phrase(message, user, message_text)
            else:
                self._handle_regular_message(message, user, message_text)
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            self._send_error_message(message, "Sorry, I couldn't process your message.")
    
    def _handle_key_phrase(self, message, user, message_text: str):
        """Handle messages containing the key phrase."""
        try:
            # Send the predefined response to the user
            self.bot.reply_to(message, self.config.KEY_RESPONSE)
            logger.info(f"Key phrase detected from user {user.id}, sent key response")
            
            # Notify the owner if configured
            if self.config.OWNER_ID:
                self._notify_owner(user, message_text, message.date)
            else:
                logger.warning("Owner notification skipped: OWNER_ID not configured")
                
        except Exception as e:
            logger.error(f"Error handling key phrase: {e}")
            raise
    
    def _handle_regular_message(self, message, user, message_text: str):
        """Handle regular messages (not containing key phrase)."""
        try:
            # Choose a random response from the list
            if self.config.OTHER_RESPONSES:
                response = random.choice(self.config.OTHER_RESPONSES)
                self.bot.reply_to(message, response)
                logger.info(f"Sent random response to user {user.id}")
            else:
                logger.warning("No other responses configured")
                self.bot.reply_to(message, "Thanks for your message!")
                
        except Exception as e:
            logger.error(f"Error handling regular message: {e}")
            raise
    
    def _notify_owner(self, user, message_text: str, message_date):
        """Send notification to the bot owner."""
        try:
            username = user.username if user.username else "No username"
            user_full_name = f"{user.first_name} {user.last_name or ''}".strip()
            
            # Format the timestamp
            if message_date:
                time_str = datetime.fromtimestamp(message_date).strftime('%Y-%m-%d %H:%M:%S UTC')
            else:
                time_str = "Unknown"
            
            notification_message = (
                "🔔 *Key Phrase Detected!*\n\n"
                f"👤 *User:* {user_full_name}\n"
                f"🆔 *User ID:* `{user.id}`\n"
                f"📝 *Username:* @{username}\n"
                f"💬 *Message:* {message_text}\n\n"
                f"🕐 *Time:* {time_str}"
            )
            
            self.bot.send_message(
                chat_id=self.config.OWNER_ID,
                text=notification_message,
                parse_mode='Markdown'
            )
            logger.info(f"Owner notification sent for user {user.id}")
            
        except Exception as e:
            logger.error(f"Failed to send owner notification: {e}")
            # Don't raise here as the main message was already sent
    
    def _send_error_message(self, message, error_text: str):
        """Send an error message to the user."""
        try:
            self.bot.reply_to(message, error_text)
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")
