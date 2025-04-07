import logging
import os
from logging.handlers import RotatingFileHandler
from config import Config

def setup_logger(name):
    """Setup logger with file and console handlers"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.getLevelName(Config.LOG_LEVEL))

    # Create formatters and add it to handlers
    format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(format_str)

    # Create a file handler
    file_handler = RotatingFileHandler(
        Config.LOG_FILE,
        maxBytes=10000000,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger