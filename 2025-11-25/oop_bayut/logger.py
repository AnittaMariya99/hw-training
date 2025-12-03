# crawler/utils/logger.py

import logging


def get_logger(name="CrawlerLogger"):
    """
    Returns a configured logger instance.
    """

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Format output
        formatter = logging.Formatter(
            "[%(levelname)s] %(asctime)s - %(name)s - %(message)s",
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        ch.setFormatter(formatter)

        # Add handler
        logger.addHandler(ch)

    return logger
