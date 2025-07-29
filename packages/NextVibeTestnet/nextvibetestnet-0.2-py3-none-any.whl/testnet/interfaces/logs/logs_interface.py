from .meta import SingletonMeta
import logging
from typing import Optional


class Logger(metaclass=SingletonMeta):
    """Custom logger that ensures a single instance (Singleton)"""

    def __init__(self, log_file: Optional[str] = "app.log"):
        """Initialize the logger and set up configurations"""
        self.logger = logging.getLogger("CustomLogger")
        self._setup(log_file)

    def _setup(self, log_file: str):
        """Configures the logger (format, handlers)"""
        if self.logger.hasHandlers():
            return  # Prevents duplicate handlers

        self.logger.setLevel(logging.INFO)

        # Define log format
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # File handler (writes logs to a file)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Console handler (outputs logs to the console)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def get_logger(self) -> logging.Logger:
        """Returns the configured logger instance"""
        return self.logger
