"""
Configuration module for the Telegram bot.
Handles environment variables and configuration validation.
"""

import os
import json
import logging
from typing import List, Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class Config:
    """Configuration class that loads settings from environment variables."""

    def __init__(self):
        """Initialize configuration by loading environment variables."""
        # Load .env file if it exists
        load_dotenv()

        # Bot configuration
        self.BOT_TOKEN: str = os.getenv('BOT_TOKEN', '')

        # Owner configuration
        owner_id_str = os.getenv('OWNER_ID', '')
        self.OWNER_ID: Optional[int] = None
        if owner_id_str:
            try:
                self.OWNER_ID = int(owner_id_str)
            except ValueError:
                logger.error(f"Invalid OWNER_ID format: {owner_id_str}")

        # Key phrase configuration
        self.KEY_PHRASE: str = os.getenv('KEY_PHRASE', 'QR код')
        self.KEY_RESPONSE: str = os.getenv(
            'KEY_RESPONSE',
            'Это то, о чём я говорил! Ура! Ты прошел мой МЕГА квест! Поздравляю! Теперь ты можешь получить свой приз!'
        )

        # Other responses configuration
        other_responses_str = os.getenv('OTHER_RESPONSES', '')
        self.OTHER_RESPONSES: List[str] = self._parse_other_responses(
            other_responses_str)

        # Bot behavior configuration
        self.CASE_SENSITIVE: bool = os.getenv('CASE_SENSITIVE',
                                              'false').lower() == 'true'

        # Logging configuration
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        self.LOG_LEVEL: str = log_level if log_level in [
            'DEBUG', 'INFO', 'WARNING', 'ERROR'
        ] else 'INFO'

        # Validate configuration
        self._validate_config()

        logger.info("Configuration initialized successfully")

    def _parse_other_responses(self, responses_str: str) -> List[str]:
        """Parse OTHER_RESPONSES from environment variable."""
        if not responses_str:
            # Default responses if none provided
            return [
                "Ты точно попал туда, куда надо?", "Что?", "Подумай ещё.",
                "Не правильно!", "Ты не угадал!"
            ]

        try:
            # Try to parse as JSON array first
            responses = json.loads(responses_str)
            if isinstance(responses, list) and all(
                    isinstance(r, str) for r in responses):
                return responses
            else:
                logger.warning(
                    "OTHER_RESPONSES is not a valid JSON array of strings")
        except json.JSONDecodeError:
            # If not JSON, try to split by delimiter
            pass

        # Try comma-separated values
        if ',' in responses_str:
            responses = [
                r.strip() for r in responses_str.split(',') if r.strip()
            ]
            if responses:
                return responses

        # Try newline-separated values
        if '\n' in responses_str:
            responses = [
                r.strip() for r in responses_str.split('\n') if r.strip()
            ]
            if responses:
                return responses

        # If all else fails, treat as single response
        return [responses_str.strip()
                ] if responses_str.strip() else self._get_default_responses()

    def _get_default_responses(self) -> List[str]:
        """Get default responses."""
        return [
            "Hello! How can I help you today?", "Thanks for your message!",
            "I'm here if you need anything else.", "Have a great day!",
            "Thanks for reaching out!"
        ]

    def _validate_config(self):
        """Validate the configuration and log warnings for missing values."""
        if not self.BOT_TOKEN:
            logger.warning("BOT_TOKEN is not set")

        if self.OWNER_ID is None:
            logger.warning("OWNER_ID is not set or invalid")

        if not self.KEY_PHRASE:
            logger.warning("KEY_PHRASE is empty, using default: 'secret'")
            self.KEY_PHRASE = 'secret'

        if not self.KEY_RESPONSE:
            logger.warning("KEY_RESPONSE is empty, using default response")
            self.KEY_RESPONSE = 'This is the prepared response for the key phrase!'

        if not self.OTHER_RESPONSES:
            logger.warning("OTHER_RESPONSES is empty, using default responses")
            self.OTHER_RESPONSES = self._get_default_responses()

        logger.info(f"Configuration validation complete:")
        logger.info(f"  - Key phrase: '{self.KEY_PHRASE}'")
        logger.info(f"  - Case sensitive: {self.CASE_SENSITIVE}")
        logger.info(f"  - Other responses count: {len(self.OTHER_RESPONSES)}")
        logger.info(f"  - Owner ID set: {self.OWNER_ID is not None}")

    def get_effective_key_phrase(self) -> str:
        """Get the key phrase in the format used for comparison."""
        return self.KEY_PHRASE if self.CASE_SENSITIVE else self.KEY_PHRASE.lower(
        )

    def normalize_text(self, text: str) -> str:
        """Normalize text for comparison based on case sensitivity setting."""
        return text if self.CASE_SENSITIVE else text.lower()
